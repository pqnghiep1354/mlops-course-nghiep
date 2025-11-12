# Sử dụng base image Python nhẹ
FROM python:3.12-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các dependencies cần thiết
RUN pip install fastapi uvicorn requests pydantic

# Sao chép ứng dụng
COPY service2_app.py .

# Thiết lập biến môi trường cho URL Service 1 (tùy chọn, để dễ debug)
ENV SERVICE1_URL http://service1:8000

# Mở cổng cho Uvicorn
EXPOSE 8001

# Chạy Uvicorn
CMD ["uvicorn", "service2_app:app", "--host", "0.0.0.0", "--port", "8001"]