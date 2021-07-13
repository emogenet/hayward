# Hayward SMART TEMP Wifi Module tools

## **TL;DR:**

This is a couple of Linux command line tools to read status from a __[Hayward heat pump smart temp wifi module](https://archive.is/wip/cLCuw)__

## **Long form:**

Where I curently live, __[Hayward](https://global.hayward.com/)__ sells swimming pool heat pumps that optionally
come with a Wifi module called "Smart Temp".

Hayward product reference is __[HWX95005010014](https://archive.is/wip/cLCuw)__

The contraption is supposed to let you control your heat pump with your phone.

In practice the thing seems to be a thin shell around some sort of standard
industrial serial controller (RS-422 or RS-485 or the like).

Said shell basically adds TCP and Wifi and wraps control data into some
sort of opaque proprietary protocol.

With a little bit of work, it can actually be made to regurgitate useful
heat pump state information and integrate those into your home automation
dashboard.

Running a cron script every 5mn on my Linux home automation server, I can
now read from the heat pump the values below and dump them into an influxdb
time series database so I can display pool status in a Grafana dashboard:

+ is the heat pump on or off?
+ what is the incoming water temperature?
+ what is the outgoing water temperature?

At this point the tools in this repo don't allow you to *control* the heat
pump, just read some of its status variables.

I have only reverse-engineered some of the data dump and none of the control
protocol because in my home, the pool heat pump is slave (via the water pressure sensor)
to a centralized pool management system that controls chemistry, filtration, temperature, etc ...
and therefore, giving direct orders to the heat pump is entirely moot since they'll be overridden.

If someone gets around to reverse-engineer more of the protocol, please submit a PR (is it MQTT? who knows.)

## In practice, the device comes with a laundry list of problems:

+ it's flaky (needs to be restarted regularly). Luckily, the electricity
  company around here is also flaky, so we get "free reboots" on a regular
  basis, it all works out :-\

+ the phone application is not particularly useful: you can't get any data
  out of it other than using your eyes to read, and much less remote control it.

+ both the "smart temp" device and the phone app are pieces of chinesium that
  hayward bough wholesale from a company called "Beijing Simple-WiFi Co.Ltd."
  the design of the system leaves a lot to be desired. Looks like security by
  shallow obscurity was the order of the day when this was designed.

+ both the data and control protocol are undocumented

+ the wifi device firmare does the following:

  + first time config:

    + set it to AP by pressing a button on the front panel
    + connect your phone or PC to it
    + go to http://192.168.2.100 to feed it useful info, such as your Wifi connection info

  + once properly configured, the device provides:

    + a web server on port 80 "protected" by a password
    + something that reads and write raw TCP on port 60000
    + when you connect to port 60000, the thing produces a continuous
      stream of data that is a dump *all* config info, including admin
      password, wifi AP password, heat pump data, the whole nine yard.
    + yes, you read correctly: that thing is a device *OUTSIDE OF YOUR HOUSE*
      that you can connect to with the press of a button (config mode) and
      that will dump all security info, including the password to your home
      router  out on port 60000. Neat isn't it?

## How the tools works:

+ just run:

        /bin/bash hpump.sh <IP address of your smart temp wifi module>

+ hpump.sh uses netcat to capture a chunk of the data stream that comes
  out of port 60000 of the wifi module and store it in a file

+ hpump.sh then runs hpump.py which parses the data dump to extract
  useful information and print it to stdout

## What the protocol look like:

+ it's a stream of binary data

+ every once in a while the device spits out a HTTP header to trick
  a browser into believing it actually speaks HTTP.

+ it then proceeds to spitting out binary data which the browser ... does what
  it can with (i.e. displays garbage).

+ data is dumped in chunks

+ all chunks start with the header 0xAA 0x5A 0xB1

+ the next two bytes are the chunk type

+ the chunk types seem to be either

        0x80 <sub type>
        0xD0 <sub type>

+ chunks of type 0x80 contains various config strings

+ chunks of type 0xD0 contains among other things data dump from sensors

+ see hpump.py for all the gory details

