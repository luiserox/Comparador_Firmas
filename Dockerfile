FROM python:3.9-slim

RUN apt-get update
RUN apt-get install -y poppler-utils
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt install imagemagick -y

WORKDIR /usr/app/src
COPY requirements.txt ./
COPY base64__ci_magick.py ./
COPY sign_detect.py ./
COPY CI.txt ./

RUN pip install -r requirements.txt

CMD [ "python", "./base64__ci_magick.py"]