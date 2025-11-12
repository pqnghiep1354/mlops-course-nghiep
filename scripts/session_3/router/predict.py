import os

import mlflow
import mlflow.sklearn
import pandas as pd
from fastapi import APIRouter

from scripts.session_3.schemas.request import HousingPredictionRequest
from scripts.session_3.schemas.response import HousingPredictionResponse

MLFLOW_TRACKING_URI = os.getenv("OUR_MLFLOW_HOST", "http://localhost:5050")
print(f"MLFLOW_TRACKING_URI: {MLFLOW_TRACKING_URI}")

mlflow.set_tracking_uri(uri=MLFLOW_TRACKING_URI)

model_name = "housing_prediction"
model_version = "1"
alias = "production"

model_uri = f"models:/{model_name}/{model_version}"

# Lazy load model - only load when needed
_model = None
housing_router = APIRouter(prefix="/housing")


def get_model():
    """Lazy load the MLflow model only when needed."""
    global _model
    if _model is None:
        _model = mlflow.sklearn.load_model(model_uri)
    return _model


# /housing/predict
@housing_router.post("/predict", response_model=HousingPredictionResponse)
def func_predict(request: HousingPredictionRequest) -> HousingPredictionResponse:
    model = get_model()
    input_data = {
        "Avg. Area Income": [request.average_area_income],
        "Avg. Area House Age": [request.average_area_house_age],
        "Avg. Area Number of Rooms": [request.average_area_number_of_rooms],
        "Avg. Area Number of Bedrooms": [request.average_area_number_of_bedrooms],
        "Area Population": [request.area_population],
    }
    df = pd.DataFrame(input_data)
    predictions = model.predict(df)
    return HousingPredictionResponse(predicted_price=predictions[0])
