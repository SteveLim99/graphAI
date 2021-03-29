FROM python:3.7.9
WORKDIR /code
RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6  -y
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN python -m pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]