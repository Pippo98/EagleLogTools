# Eagle Tools

## Overview

Eagle Log Tools is a repo with codes developed to help to **Debug**, **Save**, **Send** and **Visualize** CAN messages.
CAN bus is a protocol to send lots of data from multiple devices, so finding problems can be hard.
These tools are developed to **instantly** understand the sate of the CAN bus in general, and so of all the connected devices.

#### Features

- CAN dump rePlay
- CAN dump logging
- Real time visualization
- CSV creation from CAN dump logs

###### Developed on Chimera EVO.

![](/assets/images/0.png "Real time UI")
![](/assets/images/1.png "Real time data printing")

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
Mainly to **debug** the current state of the vehicle analyzing and parsing CAN messages.

In this folder there are different tools:
- main.py is the actual program that displays all the information about CAN data.
- csvParser.py helps to create CSV files from a CAN dump log.
- DumpSeeker.py analyzes small chunks of CAN Dump log file helping to visualize vehicle state.

# MicroPython
Folder containing Python scripts developed to help to **Send** and **Receive** CAN messages, all these codes must be deployed in MicroPython board.
- **Sender_CAN** Python code to send via UART, CAN messages (as they are).
- **Sender_JSON** Python code to send via UART, JSON structure containing parsed data coming from CAN messages.
- **Receiver** Python code to receive UART messages and forward to USB port.

# Telemetry Tools
Folder containing Python scripts developed to help to **Send**, **Save** and do some **operations via CAN** on the vehicle.

- **Sender** Python code to be used in a RaspberryPI to send JSON structure containing parsed CAN messages
- **Steering Simulator** Simulates ChimeraEVO steering wheel, so it is able to send CAN messages to the car and do all operations needed (ON OFF ...). Can be deployed in a RaspberryPI with physical CAN bus or simulated.
- **Telemetry** Python and Bash scripts to log CAN messages (CANDump) and UART GPS messages.
