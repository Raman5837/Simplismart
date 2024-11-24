FROM python:3.10-slim

# Setting the working directory in the container
WORKDIR /app

# Copying the requirements file into the container
COPY requirements.txt /app/

# Installing dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Additional ENV's
ENV PYTHONUNBUFFERED 1

EXPOSE 8000
CMD ["gunicorn", "hypervisor.wsgi:application", "--config", "gunicorn.conf.py"]