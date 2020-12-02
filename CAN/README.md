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

The other files are used as modules or are in development phase.

## main.py

![](/assets/images/0.png "Real time UI")

![](/assets/images/1.png "Real time Terminal printed Data")

These two are Screenshots that shows an example of what main.py can do.
To run this python script:
~~~bash
python3 main.py
~~~

You can choose different arguments:
1. **--def0** REAL TIME mode where the data are received via serialPort from a MicroPython or from a STM32. In this mode are enabled terminal printing and UI.
2. **--def1** Log mode where is required a file and then it is parsed in CSV. This mode disables the terminal printing and UI.
3. **--def2** Log mode where is required a file that is replayed. This mode enables terminal printing and UI.
4. **--nodisplay**  to disable UI
5. **--display**    to enable UI
6. **--noprint**    to disable terminal printing
7. **--print**      to enable terminal printing
8. **--telemetry**  to use telemetry type files that are organized in CSV in multiple folders
9. **--nodump** to enable Log mode and disable CAN dump type logs
10. **--dump**  to enable Log mode with CAN dump type logs
11. **--movie** to enable video in UI background, unstable

If no arguments are added, the default mode is like **--def0**

## csvParser.py

This program does not have any UI.
The main target is to convert multiple logs and create a CSV file for each device that has sent messages in the CAN bus logged.

To run the script open a terminal and:
~~~bash
python3 csvParser.py
~~~

This script takes as input a folder, then it automatically detect all the CAN dump log files and parse them.
The parsed files are located in the same folder chosen at the start, the it creates a subfolder for each log file (with the same name) where are located the CSV files.
At the end it compress all the CSV in a zip archive called CSV.zip located in the chosen folder.

If there are GPS logs, this program parse them, creating a CSV file located in the same folder as the other CSV files.

## Files Formatting

### CAN dump
The CAN dump file parser need a specific file formatting:

~~~
(1604665855.310219) can0 4ED#00000003FF9E0000
(1604665855.311042) can0 0D0#0700000000000000
(1604665855.311719) can0 0B0#01005B0500000000
(1604665855.312004) can0 0D0#060000000000006B
(1604665855.312766) can0 0B0#0264130588130088
(1604665855.313488) can0 4EC#0058FFF4007F0000
(1604665855.314435) can0 181#A8000001
~~~

If using can-utils (https://elinux.org/Can-utils) this formatting type is archived by running:

~~~bash
candump -Ld can0 > "$path/$filename"
~~~

This command also creates the log file.

### GPS

The GPS log is simply a log containing as first element the timestamp and then all the string coming from the GPS:

~~~
1604666371.3876646	$GNVTG,,T,,M,0.193,N,0.358,K,A*38
1604666371.3918304	$GNGGA,124212.00,4626.00810,N,01118.80473,E,1,12,0.76,234.9,M,46.0,M,,*46
1604666371.394336	$GNGSA,A,3,04,06,07,09,02,16,30,,,,,,1.39,0.76,1.16,1*07
1604666371.3966126	$GNGSA,A,3,75,65,66,76,83,,,,,,,,1.39,0.76,1.16,2*05
1604666371.398525	$GNGSA,A,3,,,,,,,,,,,,,1.39,0.76,1.16,3*0F
1604666371.4006343	$GNGSA,A,3,19,20,22,,,,,,,,,,1.39,0.76,1.16,4*02
1604666371.4036307	$GPGSV,3,1,11,02,38,275,28,03,00,129,,04,22,074,24,05,25,307,15,1*6F
1604666371.4065797	$GPGSV,3,2,11,06,33,215,24,07,70,154,27,09,59,064,14,13,00,257,,1*66
~~~

### Real Time

If the data are coming from a device connected via serialPort the data has to be formatted in the following manner:

~~~ 
timestamp   id  0   1   2   3   4   5   6   7
~~~