FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY . .

EXPOSE 5000

CMD ["python", "src/reconciler.py"]
