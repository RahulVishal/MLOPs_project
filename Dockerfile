# Use a base image
FROM python:3.12.3

RUN pip install virtualenv
ENV VIRTUAL_ENV=/venv
RUN virtualenv venv -p python3
ENV PATH="VIRTUAL_ENV/bin:$PATH"
# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port your app runs on
EXPOSE 5000

# Command to run the Flask app in production mode
CMD ["python", "app2.py", "--host=0.0.0.0", "--port=5000"]