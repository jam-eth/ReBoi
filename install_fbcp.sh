#!/bin/bash

# Update package list and install cmake
echo "Installing CMake..."
sudo apt-get update
sudo apt-get install -y cmake

# Add required configuration lines to /boot/config.txt
CONFIG_FILE="/boot/config.txt"
echo "Adding configuration lines to config.txt..."

sudo tee -a "$CONFIG_FILE" > /dev/null <<EOL
# Custom HDMI and display settings
hdmi_group=2
hdmi_mode=87
hdmi_cvt=240 220 60 1 0 0 0
hdmi_force_hotplug=1
display_rotate=1
EOL

# Set the destination directory for cloning
DEST_DIR="/home/pi/fbcp-ili9341"

# Clone the repository into /home/pi if it doesn't already exist
if [ ! -d "$DEST_DIR" ]; then
    echo "Cloning the fbcp-ili9341 repository into /home/pi..."
    git clone https://github.com/juj/fbcp-ili9341.git "$DEST_DIR"
else
    echo "Repository already exists in $DEST_DIR."
fi

# Replace gpu.cpp with the one from the script directory
SCRIPT_DIR=$(pwd)  # Get the directory where the script is running
SOURCE_FILE="$SCRIPT_DIR/gpu.cpp"  # gpu.cpp is in the same directory as the script
TARGET_FILE="$DEST_DIR/gpu.cpp"

# Check if the gpu.cpp file exists in the script directory
if [ -f "$SOURCE_FILE" ]; then
    echo "Replacing gpu.cpp with the version from $SCRIPT_DIR..."
    cp "$SOURCE_FILE" "$TARGET_FILE"
else
    echo "Error: gpu.cpp file not found in the script directory at $SOURCE_FILE."
    exit 1
fi

# Add a specific line as the second-to-last line in config.txt
echo "adding auto-run to /etc/rc.local"
sudo sed -i '$ i sudo /home/pi/fbcp-ili9341/build/fbcp-ili9341 &' /etc/rc.local


# Move into the fbcp-ili9341 directory and create/build in the build directory
cd "$DEST_DIR"
mkdir -p build
cd build

# Run cmake with specified options
echo "Running cmake with specified options..."
cmake -DILI9341=ON -DGPIO_TFT_DATA_CONTROL=23 -DGPIO_TFT_RESET_PIN=24 -DSPI_BUS_CLOCK_DIVISOR=6 -DSTATISTICS=0 ..

# Compile with make
echo "Building the project..."
make -j

# Run the executable with sudo
echo "Running fbcp-ili9341..."
sudo ./fbcp-ili9341
