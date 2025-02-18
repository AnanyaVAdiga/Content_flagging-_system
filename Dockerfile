# Step 1: Use a base image with Python
FROM python:3.12-slim

# Step 2: Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Step 3: Set working directory in the container
WORKDIR /app

# Step 4: Install Python dependencies
RUN pip install --upgrade pip 

COPY requirements.txt /app/
RUN pip install  -r requirements.txt

# Step 5: Copy the NLTK download script and run it
COPY download.py /app/
RUN python download.py  # This downloads necessary NLTK resources

# Step 6: Copy the rest of the application files
COPY . /app

# Step 7: Expose the port your app runs on
EXPOSE 5019

# Step 8: Set the default command to run your app
CMD ["python", "app.py"]
