number=0
path=/media/filippo/label/Codes/Github/EagleLogTools/CAN/test/
fname=0.log

while [ -f "$path$fname" ]; do
    number=$(( $number + 1 ))
    fname="${number}.log"
done


touch "$path""$fname"