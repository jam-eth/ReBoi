#!/bin/bash

# Update package list and install cmake
echo "Installing CMake..."
sudo apt-get update
sudo apt-get install -y cmake

# Navigate to the home directory
cd ~

# Clone the repository if it doesn’t already exist
REPO_URL="https://github.com/juj/fbcp-ili9341.git"
REPO_DIR="fbcp-ili9341"
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning the fbcp-ili9341 repository..."
    git clone "$REPO_URL"
else
    echo "Repository already exists."
fi

# Replace gpu.cpp with the one from the ReBoi directory
REPLACEMENT_DIR="ReBoi"
SOURCE_FILE="$REPLACEMENT_DIR/gpu.cpp"
TARGET_FILE="$REPO_DIR/gpu.cpp"

if [ -f "$SOURCE_FILE" ]; then
    echo "Replacing gpu.cpp with the version from ReBoi..."
    cp "$SOURCE_FILE" "$TARGET_FILE"
else
    echo "Replacement gpu.cpp file not found in ReBoi directory."
    exit 1
fi

# Move into the fbcp-ili9341 directory and create/build in the build directory
cd "$REPO_DIR"
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
