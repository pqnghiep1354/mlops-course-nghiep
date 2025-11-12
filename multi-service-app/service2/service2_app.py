from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# URL của Service 1, sử dụng tên service trong docker-compose
SERVICE1_URL = os.environ.get("SERVICE1_URL", "http://service1:8000")

class CalculationRequest(BaseModel):
    number1: int
    method: str  # "add", "subtract", "multiply", "divide"

@app.post("/calculate")
def calculate(request: CalculationRequest):
    """
    Tính toán bằng cách lấy tham số thứ hai từ Service 1.
    """
    try:
        # 1. Gọi Service 1 để lấy thông số thứ hai
        response = requests.get(f"{SERVICE1_URL}/read_file")
        response.raise_for_status()  # Ném lỗi cho mã trạng thái HTTP xấu

        data = response.json()
        number2 = data.get("number")
        
        if number2 is None or not isinstance(number2, int):
            return {"error": "Could not retrieve a valid integer from Service 1"}

        result = 0
        
        # 2. Thực hiện tính toán
        if request.method == "add":
            result = request.number1 + number2
        elif request.method == "subtract":
            result = request.number1 - number2
        elif request.method == "multiply":
            result = request.number1 * number2
        elif request.method == "divide":
            if number2 == 0:
                return {"error": "Cannot divide by zero (number2 is 0)"}
            result = request.number1 / number2
        else:
            return {"error": f"Invalid method: {request.method}. Must be add, subtract, multiply, or divide"}
            
        return {
            "number1": request.number1,
            "number2_from_service1": number2,
            "method": request.method,
            "result": result
        }

    except requests.exceptions.ConnectionError:
        return {"error": f"Could not connect to Service 1 at {SERVICE1_URL}. Is it running?"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error from Service 1: {e}"}
    except Exception as e:
        return {"error": str(e)}