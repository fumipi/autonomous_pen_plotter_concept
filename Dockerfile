# Use the official Webot base image
FROM cyberbotics/webots.cloud:R2023b

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies from requirements.txt
RUN pip3 install -r requirements.txt

# Set the working directory inside the container
WORKDIR /usr/local/webots-project

# Copy your simulation files to the container
COPY . .

# Specify the command to run your simulation
CMD ["webots", "--mode=stop", "worlds/penbot.wbt"]