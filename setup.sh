#!/bin/bash

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3
sudo apt-get install -y python3-pip
# Numpy and scapy is too slow to install with pip, so we use apt-get
sudo apt-get install python3-numpy
sudo apt-get install python3-scapy
sudo pip3 install -r requirements.txt
