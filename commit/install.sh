#!/bin/sh

# install all requirements present on requirements.txt file using pip3
install_requirements() {
  echo 'Starting installation...'
  pip3 install -r requirements.txt
  echo 'Needed packages have been installed'
}


if ! type pip3 > /dev/null; then
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo 'Installing pip3 to continue with the installation of requirements...'
    sudo apt-get install python3-pip
    install_requirements
  else
    echo 'You need to install pip3 to continue with this instalation'
  fi
else
  install_requirements
fi