#!/usr/bin/env bash

#device="pi@192.168.43.131"         ## MY PI4
#device="ubuntu@192.168.8.101"      ## TELEMETRY pwd telemetrypi
device="root@192.168.8.102"         ## STEERING  pwd eaglepi

FOLDERNAME="$(date +"%d-%b-%Y__%H-%M-%S")"

echo $FOLDERNAME

ssh $device "
cd ~/logs &&
tar -czvf $FOLDERNAME'.tar.gz' *.log &&
mkdir '$FOLDERNAME' &&
mv *.log $FOLDERNAME"

scp $device:~/logs/*.tar.gz /home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER

ssh $device "rm ~/logs/$FOLDERNAME.tar.gz"