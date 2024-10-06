FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install required system packages (Chrome and other dependencies)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libatk-bridge2.0-0 \
    libxkbcommon-x11-0 \
    libgtk-3-0 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Download and install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -fy install

# Download ChromeDriver and place it in /usr/local/bin
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -N https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip && \
    chmod +x chromedriver && \
    mv chromedriver /usr/local/bin/

# Set the working directory
WORKDIR /usr/src/app

# Copy the project files into the container
COPY . /usr/src/app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port for the Flask app
EXPOSE 5000

# Set the Flask app environment variables
ENV FLASK_APP=scraper_api.py
ENV FLASK_ENV=development

# Command to run Flask API
CMD ["flask", "run", "--host=0.0.0.0"]
