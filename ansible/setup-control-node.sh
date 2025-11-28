#!/bin/bash
# Setup Ansible Control Node
# This script installs Ansible and dependencies for orchestrating the AI stack deployment

set -e

echo "============================================"
echo "Setting up Ansible Control Node"
echo "============================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# Update package lists
echo "[1/5] Updating package lists..."
$SUDO apt-get update -q

# Install Ansible and dependencies
echo "[2/5] Installing Ansible and dependencies..."
$SUDO apt-get install -y \
    ansible \
    python3-pip \
    sshpass \
    git

# Install Ansible collections
echo "[3/5] Installing Ansible collections..."
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.general

# Install Python packages
echo "[4/5] Installing Python Docker libraries..."
pip3 install --user docker docker-compose PyYAML

# Verify installation
echo "[5/5] Verifying installation..."
echo ""
echo "Ansible version:"
ansible --version | head -1
echo ""
echo "Python Docker library:"
python3 -c "import docker; print(f'✅ docker: {docker.__version__}')"
echo ""
echo "Ansible collections:"
ansible-galaxy collection list | grep -E 'community.docker|community.general'
echo ""

echo "============================================"
echo "✅ Ansible Control Node Setup Complete"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Test Ansible connectivity:"
echo "   ansible -i inventory-minimal.yml all -m ping"
echo ""
echo "2. Deploy shared AI infrastructure:"
echo "   ansible-playbook -i inventory-minimal.yml 02-deploy-shared-ai-minimal.yml"
echo ""
echo "3. Deploy user services:"
echo "   ansible-playbook -i inventory-minimal.yml 06-deploy-user-services-minimal.yml"
echo ""
