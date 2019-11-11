FROM python:alpine
MAINTAINER Alexander Puzynia <werwolf.by@gmail.com>

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY dhealer /app/dhealer
COPY run.py /app

WORKDIR /app

CMD ["python", "run.py"]