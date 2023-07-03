#!/bin/bash

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3
sudo apt-get install -y python3-pip
sudo pip3 install -r requirements.txt
