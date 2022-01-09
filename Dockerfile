FROM python:bullseye
RUN apt-get update
WORKDIR /usr/src/app

COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt 

COPY . .
EXPOSE 5000
WORKDIR /usr/src/app/spotifylocation
CMD ["gunicorn","--env", "SCRIPT_NAME=/spotify", "-b", "0.0.0.0:5000", "app:app"]