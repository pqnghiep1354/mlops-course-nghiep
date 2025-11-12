from fastapi import FastAPI
import os

app = FastAPI()

# Đường dẫn đến file được mount
FILE_PATH = os.environ.get("NUMBER_FILE_PATH", "/app/number.txt")

@app.get("/read_file")
def read_number_from_file():
    """Đọc giá trị số nguyên từ file number.txt."""
    try:
        with open(FILE_PATH, 'r') as f:
            number = f.read().strip()
            # Đảm bảo giá trị đọc được là số nguyên
            return {"number": int(number)}
    except FileNotFoundError:
        return {"error": f"File not found at {FILE_PATH}"}
    except ValueError:
        return {"error": "File content is not a valid integer"}
    except Exception as e:
        return {"error": str(e)}

# Bạn cần một file requirements.txt đơn giản nếu muốn cài FastAPI riêng
# Nhưng ở đây, ta sẽ cài trực tiếp trong Dockerfile để đơn giản hóa.
# Nếu bạn muốn tách ra, hãy thêm 'fastapi' và 'uvicorn' vào service1/requirements.txt.