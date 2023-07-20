# Use the official Python image as the base image.
FROM python:3.9

# Set environment variables.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies.
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the Django project files into the container.
COPY . /app/

# Collect static files.
RUN python manage.py collectstatic --noinput

# Expose the port your Django app runs on.
EXPOSE 8000

# Run the Django development server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
