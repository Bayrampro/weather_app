
FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN python manage.py collectstatic --noinput
RUN python manage.py migrate


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "weather_project.wsgi:application"]
