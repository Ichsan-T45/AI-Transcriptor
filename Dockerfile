FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y ffmpeg libavcodec-extra && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir uploads

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 80

CMD ["python", "app.py"]