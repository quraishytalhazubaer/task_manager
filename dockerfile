# Use Python 3.9 as base image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for Flask
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]
