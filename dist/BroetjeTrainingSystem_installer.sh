#!/bin/bash
# Broetje Training System Installer

INSTALL_DIR="/opt/broetje-training"
DESKTOP_FILE="/usr/share/applications/broetje-training.desktop"
EXEC_LINK="/usr/local/bin/broetje-training"

echo "Installing Broetje Training System..."

# Create installation directory
sudo mkdir -p "$INSTALL_DIR"

# Copy executable
sudo cp BroetjeTrainingSystem "$INSTALL_DIR/"

# Make executable
sudo chmod +x "$INSTALL_DIR/BroetjeTrainingSystem"

# Create symbolic link
sudo ln -sf "$INSTALL_DIR/BroetjeTrainingSystem" "$EXEC_LINK"

# Create desktop entry
sudo tee "$DESKTOP_FILE" > /dev/null << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Broetje Training System
Comment=Interactive training system for controls engineers
Exec=$INSTALL_DIR/BroetjeTrainingSystem
Icon=broetje-training
Terminal=false
Categories=Education;Training;
EOF

# Update desktop database
sudo update-desktop-database

echo "Installation complete!"
echo "You can now run 'broetje-training' from terminal or find it in your applications menu."
