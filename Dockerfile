FROM python:3.8-slim-buster

# USER app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# RUN mkdir /db
#RUN chown app:app -R /db

RUN mkdir /code
WORKDIR /code



RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev  \
    # && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


ADD requirements.txt /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN pip install psycopg2-binary

# Copy the current directory contents into the container at /app
COPY . /code/

# Collect static files
# RUN python ubiquote/manage.py collectstatic --noinput

# EXPOSE 8000

# Run the application
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ubiquote.wsgi:application"]

# ADD . /code/