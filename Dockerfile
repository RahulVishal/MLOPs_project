# Use a base Python image
FROM python:3.12.3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn (WSGI server for production)
RUN pip install gunicorn

# Copy the application files
COPY . .

# Expose the port Flask will run on
EXPOSE 5001

# Command to run the application using gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app2:app"]