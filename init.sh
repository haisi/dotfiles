#!/usr/bin/env bash
set -e

echo "[i] Ask for sudo password"
sudo -v

case "$(uname -s)" in
    Darwin)
        # install Command Line Tools
        if [[ ! -x /usr/bin/gcc ]]; then
          echo "[i] Install macOS Command Line Tools"
          xcode-select --install
        fi

        # install homebrew
        if [[ ! -x /opt/homebrew/bin/brew ]]; then
          echo "[i] Install Homebrew"
          /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
          (echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> /Users/hak/.bash_profile
          (echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> /Users/hak/.zprofile
          eval "$(/opt/homebrew/bin/brew shellenv)"
        fi

        # install ansible
        if [[ ! -x /usr/local/bin/ansible ]]; then
            echo "[i] Install Ansible"
            brew install ansible
        fi

        # set macos defaults
        echo "[i] Set some specific macOS settings"
        set +e
        ./macos.bash
        set -e
        ;;

        Linux)
        if [ -f /etc/os-release ]
            then
                . /etc/os-release

                # actually, no Linux support implemented yet

                case "$ID" in
                    debian | ubuntu)
                        if [[ ! -x /usr/bin/ansible ]]; then
                            echo "[i] Install Ansible"
                            sudo apt-get install -y ansible
                        fi
                        ;;

                    arch)
                        if [[ ! -x /usr/bin/ansible ]]; then
                            echo "[i] Install Ansible"
                            sudo pacman -S ansible --noconfirm
                        fi
                        ;;

                    *)
                        echo "[!] Unsupported Linux Distribution: $ID"
                        exit 1
                        ;;
                esac
            else
                echo "[!] Unsupported Linux Distribution"
                exit 1
            fi
        ;;
    *)
        echo "[!] Unsupported OS"
        exit 1
        ;;
esac

# Install requirements, i.e. third party Ansible modules for mac
echo "[i] Install ansible-galaxy modules"
ansible-galaxy install -r requirements.yml

# Run main playbook
echo "[i] Run Playbook"
ansible-playbook main.yml --ask-become-pass

# For account to use zsh
chsh -s /bin/zsh
