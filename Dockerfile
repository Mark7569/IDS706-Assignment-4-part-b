FROM python:3.13-slim
WORKDIR /app
ENV MPLBACKEND=Agg MPLCONFIGDIR=/tmp/matplotlib PYTHONDONTWRITEBYTECODE=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home analyst
COPY gold_analysis ./gold_analysis
USER analyst
ENTRYPOINT ["python", "-m", "gold_analysis"]
