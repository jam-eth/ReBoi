#!/bin/bash

# Define target labels for the USB drive
TARGET_LABELS=("RPI-RP2" "CIRCUITPY")

# Function to find the USB drive with the specified labels
find_usb_drive() {
    echo "Detecting USB drives..."
    lsblk -f
    MOUNTPOINT=$(lsblk -f | awk '/RPI-RP2|CIRCUITPY/ {print $NF}')
    DRIVE_LABEL=$(lsblk -f | awk '/RPI-RP2|CIRCUITPY/ {print $3}')

    if [ -n "$MOUNTPOINT" ] && [ -n "$DRIVE_LABEL" ]; then
    echo "Found USB drive with label $DRIVE_LABEL mounted at $MOUNTPOINT."
    else
    echo "Error: USB drive with labels RPI-RP2 CIRCUITPY not found."
    exit 1
    fi
    done

    if [ -z "$MOUNT_POINT" ]; then
        echo "Error: USB drive with labels ${TARGET_LABELS[@]} not found."
        exit 1
    fi

    echo "Found USB drive with label '$DETECTED_LABEL' mounted at $MOUNT_POINT."
}

# Copy the .uf2 file to the RPI-RP2 drive
copy_to_rpi_rp2() {
    echo "Copying adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.0.uf2 to $MOUNT_POINT..."
    cp "adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.0.uf2" "$MOUNT_POINT"
    echo "File copied. Waiting for the drive to remount as CIRCUITPY..."
    for ((i = 1; i <= 45; i++)); do
        echo -n "."
        sleep 1
    done
    echo
}

# Copy files to the CIRCUITPY drive
copy_to_circuitpy() {
    echo "Copying files to CIRCUITPY at $MOUNT_POINT..."
    SCRIPT_DIR=$(pwd)  # Get the directory where the script is running
    FILES=("display_init.py" "usb_keypad.py" "mode_controller.py" "code.py")
    for FILE in "${FILES[@]}"; do
        if [ -f "$SCRIPT_DIR/$FILE" ]; then
            cp "$SCRIPT_DIR/$FILE" "$MOUNT_POINT"
            echo "Copied $FILE to CIRCUITPY."
        else
            echo "Warning: $FILE not found in $SCRIPT_DIR."
        fi
    done
    echo "All files copied to CIRCUITPY."
}

# Main Script Logic for USB handling
echo "Detecting USB drive..."
find_usb_drive

if [ "$DETECTED_LABEL" == "RPI-RP2" ]; then
    copy_to_rpi_rp2
    echo "Rechecking for CIRCUITPY..."
    find_usb_drive
    if [ "$DETECTED_LABEL" == "CIRCUITPY" ]; then
        copy_to_circuitpy
    else
        echo "Error: CIRCUITPY drive not found after flashing RPI-RP2."
        exit 1
    fi
elif [ "$DETECTED_LABEL" == "CIRCUITPY" ]; then
    copy_to_circuitpy
else
    echo "Unexpected drive label detected: $DETECTED_LABEL."
    exit 1
fi

# FBCP-ILI9341 Setup Logic
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
echo "Adding auto-run to /etc/rc.local"
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

# Configure triggerhappy
TRIGGER_CONF_FILE="$SCRIPT_DIR/custom.conf"
TRIGGER_CONF_DEST="/etc/triggerhappy/triggers.d/"
if [ -f "$TRIGGER_CONF_FILE" ]; then
    echo "Copying $TRIGGER_CONF_FILE to $TRIGGER_CONF_DEST..."
    sudo cp "$TRIGGER_CONF_FILE" "$TRIGGER_CONF_DEST"
    echo "Triggerhappy configuration updated."
else
    echo "Warning: $TRIGGER_CONF_FILE not found in $SCRIPT_DIR. Triggerhappy configuration not updated."
fi

# Run the executable with sudo
echo "Running fbcp-ili9341..."
sudo ./fbcp-ili9341

echo "Operation complete."

