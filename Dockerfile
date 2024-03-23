# Use an official Python runtime as a parent image
FROM python:3.12.2-bullseye

RUN apt-get update && apt-get install -y libgl1-mesa-glx


# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into container at /app
ADD flask_app /app
ADD requirements.txt /app
RUN ls /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Define volumes
VOLUME /app/collected_data

# Run flask_app.py when the container launches
CMD ["gunicorn", "-k", "eventlet", "-w", "2", "-b", "0.0.0.0:5000", "run_app:app"]

#docker run --env-file=.env your_image_name