FROM python:3.8.5
WORKDIR /code
RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6  -y
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN python -m pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5001
COPY . .
CMD ["flask", "run", "--port=5001"]