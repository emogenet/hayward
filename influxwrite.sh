#!/bin/bash

# write a sample to an influxdb server
# note that server IP:Port is hard-coded in curl statement below
# change according to your needs

zone="$1"
label="$2"
value="$3"
label=$(echo "$label" | sed -e's/ /_/g' | sed -e's/\.//g')

curl                                                            \
    -i                                                          \
    -XPOST 'http://192.168.1.100:8086/write?db=heater'          \
    --data-binary "$zone"_"$label value=$value" >& /dev/null    \

