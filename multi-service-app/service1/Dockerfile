# Sử dụng base image Python nhẹ
FROM python:3.12-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt FastAPI và Uvicorn
RUN pip install fastapi uvicorn

# Sao chép ứng dụng
COPY service1_app.py .

# Thiết lập biến môi trường cho đường dẫn file (dành cho việc mount)
ENV NUMBER_FILE_PATH /app/number.txt

# Mở cổng cho Uvicorn
EXPOSE 8000

# Chạy Uvicorn khi container khởi động
# --host 0.0.0.0 là bắt buộc để container lắng nghe các kết nối bên ngoài
CMD ["uvicorn", "service1_app:app", "--host", "0.0.0.0", "--port", "8000"]