# Telemetry Tools

## Overview

Is a repo with python scripts developed to help to **Send**, **Save** and do some **operations via CAN** on the vehicle.

#### Folders

- **Sender** Python code to be used in a RaspberryPI to send JSON structure containing parsed CAN messages
- **Steering Simulator** Simulates ChimeraEVO steering wheel, so it is able to send CAN messages to the car and do all operations needed (ON OFF ...). Can be deployed in a RaspberryPI with physical CAN bus or simulated.
- **Telemetry** Python and Bash scripts to log CAN messages (CANDump) and UART GPS messages.

###### Developed and Tested on Chimera EVO.

## Installation

Make sure you have followed all the steps in the *main folder*.

Install can-utils package 
~~~bash
sudo apt-get install can-utils
~~~

If using these codes with CAN in simulation mode, so 'vcan0' device, make sure to **run vcanSetup**:

~~~bash
chmod 777 vcanSetup
./vcanSetup
~~~

**Now** you have initialized CAN virtual device:

# Sender

Code to send JSON data via UART.
Tested with RaspberryPI with UART antenna connected (HC-12)

run:
~~~bash
python3 main.py
~~~

# Steering Simulator

Code to simulate Chimera EVO steering wheel.
run:
~~~bash
python3 steeringSimulator.py
~~~
If using virtual CAN device is useful to re-play a CAN Dump log, to do that
~~~bash
python3 dumpSimulator.py
~~~
Here is requested to select a file formatted like:
~~~
(1604665855.310219) can0 4ED#00000003FF9E0000
(1604665855.311042) can0 0D0#0700000000000000
(1604665855.311719) can0 0B0#01005B0500000000
(1604665855.312004) can0 0D0#060000000000006B
(1604665855.312766) can0 0B0#0264130588130088
(1604665855.313488) can0 4EC#0058FFF4007F0000
(1604665855.314435) can0 181#A8000001
~~~
That is guaranteed if using these **Telemetry** codes.

# Telemetry

Bash and python scripts to generate CAN Dump log files and GPS log files.

First make executable all the files:
~~~bash
chmod 777 Telemetry/*
~~~
Then to start logging (both CAN Dump and UART):
~~~bash
./startLogging
~~~
To interrupt run:
~~~bash
./interrupt
~~~
**NB** this last command **kills** all the python3 processes.

The default folder is:
*"/home/ubuntu/logs/"*
To change it please change in all scripts.