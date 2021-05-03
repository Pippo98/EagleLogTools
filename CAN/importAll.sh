#!/usr/bin/env bash

#device="pi@192.168.43.131"         ## MY PI4
#device="ubuntu@192.168.8.102"      ## TELEMETRY pwd telemetrypi
#device="ubuntu@192.168.8.101"      ## TELEMETRY pwd telemetrypi
device="ubuntu@192.168.8.101"      ## TELEMETRY pwd telemetrypi
#device="root@192.168.8.102"         ## STEERING  pwd eaglepi
#device="filippo@192.168.1.180"

FOLDERNAME="$(date +"%d-%b-%Y__%H-%M-%S")"
SOURCEPATH="~/logs/"
DESTPATH="/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/"

echo $FOLDERNAME

# ssh $device "
# cd ~/logs &&
# mkdir '$FOLDERNAME' &&
# mv *.log $FOLDERNAME"

# scp -r $device:~/logs/$FOLDERNAME /home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER


ssh $device "
cd ~/logs &&
zip $FOLDERNAME'.zip' *.log &&
rm *.log"

scp $device:~/logs/$FOLDERNAME'.zip' $DESTPATH

unzip $DESTPATH$FOLDERNAME'.zip' -d $DESTPATH$FOLDERNAME
rm $DESTPATH$FOLDERNAME'.zip'
