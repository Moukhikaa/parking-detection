FROM python:3.11.0

#
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
#
COPY ./app /app

#
CMD ["fastapi", "run", "main.py", "--port", "80"]