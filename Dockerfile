FROM python:3.9-slim

RUN apt-get update
RUN apt-get install -y poppler-utils
RUN apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /usr/app/src
COPY requirements.txt ./
COPY base64_to_pdf.py ./
COPY pagare.pdf ./
COPY ci1.jpeg ./

RUN pip install -r requirements.txt

CMD [ "python", "./base64_to_pdf.py"]