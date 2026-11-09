FROM python:3.12-slim

WORKDIR /app

COPY backend ./backend
COPY demo_system ./demo_system

ENV HOST=0.0.0.0
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "backend/main.py"]
