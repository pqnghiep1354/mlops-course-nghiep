import logging
import os
from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Set MLflow tracking URI. Using a local file-based store is common for local development.
mlflow.set_tracking_uri("file:./mlruns")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def train():
    mlflow.set_experiment("housing_price_training")

    # Paths
    PROJECT_ROOT = Path(os.getcwd())
    DATA_PATH = PROJECT_ROOT / "data" / "housing.csv"
    ARTIFACT_DIR = PROJECT_ROOT / "artifacts"
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH = ARTIFACT_DIR / "housing_linear_sgd.joblib"

    logger.info(f"Data path: {DATA_PATH}")

    logger.info("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")

    logger.info("Preparing features and target...")
    # Identify target and basic features from the CSV header
    TARGET = "Price"
    NUM_FEATURES = [
        "Avg. Area Income",
        "Avg. Area House Age",
        "Avg. Area Number of Rooms",
        "Avg. Area Number of Bedrooms",
        "Area Population",
    ]

    X = df[NUM_FEATURES]
    y = df[TARGET]

    logger.info("Splitting train/test...")
    test_split_ratio = 0.2
    data_split_random_state = 42
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_split_ratio, random_state=data_split_random_state)

    # Model Hyperparameters
    model_params = {
        "max_iter": 5000,
        "tol": 1e-3,
        "learning_rate": "optimal",
        "random_state": 20,
    }

    logger.info("Building pipeline...")
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUM_FEATURES),
        ],
        remainder="drop",
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("regressor", SGDRegressor(**model_params)),
        ]
    )

    logger.info("Training model...")
    with mlflow.start_run(run_name="sgd_regressor_training"):
        # Log all parameters from the dictionary
        mlflow.log_params(model_params)
        mlflow.log_param("features", NUM_FEATURES)
        mlflow.log_param("target", TARGET)
        mlflow.log_param("test_split_ratio", test_split_ratio)
        mlflow.log_param("data_split_random_state", data_split_random_state)

        model.fit(X_train, y_train)

        # Evaluate model performance
        logger.info("Evaluating model performance...")

        # Make predictions on training and test sets
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        # Calculate metrics for training set
        train_mse = mean_squared_error(y_train, y_train_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        train_rmse = train_mse**0.5

        # Calculate metrics for test set
        test_mse = mean_squared_error(y_test, y_test_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        test_rmse = test_mse**0.5

        # Log training metrics
        logger.info("Training set metrics:")
        logger.info(f"  MSE: {train_mse:.4f}")
        logger.info(f"  MAE: {train_mae:.4f}")
        logger.info(f"  R²: {train_r2:.4f}")
        logger.info(f"  RMSE: {train_rmse:.4f}")

        # Log test metrics
        logger.info("Test set metrics:")
        logger.info(f"  MSE: {test_mse:.4f}")
        logger.info(f"  MAE: {test_mae:.4f}")
        logger.info(f"  R²: {test_r2:.4f}")
        logger.info(f"  RMSE: {test_rmse:.4f}")
        
        # Log all metrics to MLflow in one call
        metrics = {
            "train_mse": train_mse,
            "train_mae": train_mae,
            "train_r2": train_r2,
            "train_rmse": train_rmse,
            "test_mse": test_mse,
            "test_mae": test_mae,
            "test_r2": test_r2,
            "test_rmse": test_rmse,
        }
        mlflow.log_metrics(metrics)

        # Save the model locally
        joblib.dump(model, MODEL_PATH)
        logger.info(f"Model saved to: {MODEL_PATH}")
        
        # Log the local model file as an artifact
        mlflow.log_artifact(str(MODEL_PATH), "model_files")

        # Log the model to MLflow, including registration in the Model Registry
        mlflow.sklearn.log_model(model, "model", registered_model_name="housing_price_predictor_sgd_v2")


if __name__ == "__main__":
    train()
