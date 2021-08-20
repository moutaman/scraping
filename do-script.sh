#!/bin/bash

sudo apt update -y
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt update -y
apt install docker-ce -y
apt install docker-compose -y

apt install git python3-pip  -y

pip install cookiecutter

cookiecutter gh:TeamHG-Memex/aquarium

cd ./aquarium
docker-compose up
