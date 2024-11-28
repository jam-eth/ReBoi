#!/bin/bash

SCRIPT_DIR=$(pwd)

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
hdmi_cvt=480 440 60 1 0 0 0
hdmi_force_hotplug=1
display_rotate=1
EOL

# Detect USB drives with specific labels
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

# If the detected drive is RPI-RP2, copy the UF2 file
if [ "$DRIVE_LABEL" == "RPI-RP2" ]; then
    echo "Copying UF2 file to $MOUNTPOINT..."
    SCRIPT_DIR=$(pwd)
    cp "$SCRIPT_DIR/adafruit-circuitpython-raspberry_pi_pico-en_US-9.2.0.uf2" "$MOUNTPOINT"
    echo "Waiting for the device to reboot..."
    for i in {1..45}; do
        echo -n "."
        sleep 1
    done
    echo ""
    # Re-run detection to find CIRCUITPY
    MOUNTPOINT=$(lsblk -f | awk '/CIRCUITPY/ {print $NF}')
    if [ -n "$MOUNTPOINT" ]; then
        echo "Device rebooted and CIRCUITPY detected at $MOUNTPOINT."
    else
        echo "Error: CIRCUITPY not detected after reboot."
        exit 1
    fi
fi

# If the detected drive is CIRCUITPY, copy the Python files
if  [ "$DRIVE_LABEL" == "CIRCUITPY" ]; then
    echo "Copying Python files to $MOUNTPOINT..."
    cp "$SCRIPT_DIR/display_init.py" "$MOUNTPOINT"
    cp "$SCRIPT_DIR/usb_keypad.py" "$MOUNTPOINT"
    cp "$SCRIPT_DIR/mode_controller.py" "$MOUNTPOINT"
    cp "$SCRIPT_DIR/code.py" "$MOUNTPOINT"
    echo "Python files copied successfully."
fi

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
SOURCE_FILE="$SCRIPT_DIR/gpu.cpp"
TARGET_FILE="$DEST_DIR/gpu.cpp"

if [ -f "$SOURCE_FILE" ]; then
    echo "Replacing gpu.cpp with the version from $SCRIPT_DIR..."
    cp "$SOURCE_FILE" "$TARGET_FILE"
else
    echo "Error: gpu.cpp file not found in the script directory at $SOURCE_FILE."
    exit 1
fi

# Add a specific line as the second-to-last line in /etc/rc.local
echo "Adding auto-run to /etc/rc.local..."
sudo sed -i '$ i sudo /home/pi/fbcp-ili9341/build/fbcp-ili9341 &' /etc/rc.local

# Move into the fbcp-ili9341 directory and create/build in the build directory
cd "$DEST_DIR"
mkdir -p build
cd build

echo "Running cmake with specified options..."
cmake -DILI9341=ON -DGPIO_TFT_DATA_CONTROL=23 -DGPIO_TFT_RESET_PIN=24 -DSPI_BUS_CLOCK_DIVISOR=6 -DSTATISTICS=0 ..

echo "Building the project..."
make -j

echo "Running fbcp-ili9341..."
sudo ./fbcp-ili9341

# Configure TriggerHappy
echo "Configuring TriggerHappy..."

# Create a temporary file for the new service configuration
temp_file=$(mktemp)

# Add the configuration to the temporary file
cat <<EOF > "$temp_file"
[Service]
ExecStart=
ExecStart=/usr/sbin/thd --triggers /etc/triggerhappy/triggers.d/ --socket /run/thd.socket --user pi --deviceglob /dev/input/event*
EOF

# Use sudo to copy the file content into the systemd override
sudo systemctl edit --full triggerhappy.service < "$temp_file"

# Clean up the temporary file
rm -f "$temp_file"

echo "Restarting TriggerHappy service..."
sudo systemctl daemon-reload
sudo systemctl restart triggerhappy
echo "TriggerHappy configured successfully."
