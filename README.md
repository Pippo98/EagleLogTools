# Eagle Tools

## Overview

Eagle Log Tools is a repo with python scripts developed to help to **Debug** and **Visualize** CAN messages.

#### Features

- CAN dump rePlay.
- Real time visualization
- CSV creation from CAN dump logs

###### Developed on Chimera EVO.

## Installation

Make sure you have python3:

~~~bash
python3 --version
~~~

To install python3 please run:
~~~bash
sudo apt-get update
sudo apt-get install python3.6
~~~

To install python requirements use pip3, to install pip3 run:
~~~bash
sudo apt-get install python3-pip
~~~

__Now__ you are ready to install all python modules, to do that run:

~~~bash
pip3 install -r requirements.txt
~~~

The last thing is to install other modules from a github repo, to do that go to:
https://github.com/Pippo98/ownModules.git
and follow the instructions.

# CAN

In this folder there are two different tools:
1. main.py is the actual program that displays all the information about CAN data.
2. csvParser.py helps to create CSV files from a CAN dump log.

# MicroPython
Folder containing Python scripts developed to help to **Send** and **Receive** CAN messages, all these codes must be deployed in MicroPython board.

# Telemetry
Folder containing Python scripts developed to help to **Send**, **Save** and do some **operations via CAN** on the vehicle.