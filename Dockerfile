FROM python:3.14-slim
WORKDIR /app/
COPY pyproject.toml .
RUN pip install .
COPY src ./src/
COPY regression_cases ./regression_cases/

CMD ["python", "src/main.py"]



