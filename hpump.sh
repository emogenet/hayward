#!/bin/bash

# grab and parse data from a hayward smart temp device

heatpump="$1"

if test -z "$heatpump"
then
    echo "usage: /bin/bash <ip address of your wifi module>"
    exit 1
fi

# grab
echo 'capturing raw binary stream from heat pump wifi module ...' $heatpump:60000
nc -N -W 10 $heatpump 60000 >./raw.bin || (echo 'netcat failed ... maybe install it?'; exit 1)
echo done.
echo

# parse
echo 'parsing binary strem to extract relevnt info ...'
echo
python3 hpump.py || (echo 'python3 failed ... maybe install it?'; exit 1)
rm -f raw.bin
echo done.
echo

