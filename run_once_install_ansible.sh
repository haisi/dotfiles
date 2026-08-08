#!/bin/bash
set -eu

sudo apt-get update
sudo apt-get install -y ansible

ansible-playbook "$HOME/.bootstrap/setup.yml" --ask-become-pass

echo "Ansible bootstrap complete."
