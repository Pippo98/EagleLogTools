# Odometer
Receives Kilometers and wheel rotations via CAN message, stores the values in a .file and at the start sends the last status saved.


# Messages
## New Run
To start a new counter send:  
~~~
0D3#00
~~~
The payload is not important  
The counter will start from 0  

## Update
To update counter send:
~~~
0D1#<payload>
~~~
Payload is composed by 6 bytes.  
The firsts 3 bytes are for wheel rotations. **BIG endian** system.  
The lasts  3 bytes are for Kilometers. The value must be sent in meters, will be stored in Kilometers. **BIG endian** system.  

## Send
When the program starts it sends the last values stored using the message:  
~~~
0D2#<payload>
~~~
Payload (3 bytes) represents wheel rotations expressed in **BIG endian** system.  

## Request
There isn't a request message for the last status but by sending a smaller value of rotations than the one saved will cause a resend of last status.  

## File format
The file is saved in the home folder '~'.  
The file name is '.odometer'.  
File example:  
~~~
start;end;rotations;km;
1620137003.9185843;1620137003.918586;0;0;
1620137021.2392533;1620137028.958582;9;0.006;
~~~
It's formatted as a CSV file.  
**start** timestamp of the start command  
**end**   timestamp of the last update  
