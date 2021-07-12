#!/usr/bin/python3

# parse data from a hayward smart temp device

import binascii

# debug
def isprint(
    x
):
    return (0x20<=x and x<0x7F)

# debug
def decimal(
    byteArray
):

    return

    i = 0
    s = 'decimal:'
    for x in byteArray:
        if (9==i or 10==i):
            ox = x
            x *=  0.5
            x -= 30.0
            s += ' %4d(=%.2f) ' % (ox, x)
        elif 11==i:
            ox = x
            x *= 4.0
            x -= 316.0
            s += ' %4d(=%.2f) ' % (ox, x)
        elif 31==i:
            ox = x
            #x /= -15.0
            #x +=  40.0
            x *= -0.075
            x +=  41.0
            s += ' %4d(=%.2f) ' % (ox, x)
        else:
            s += '%4d' % x
        i += 1
    return s

# debug
def quoted(
    byteArray
):
    array = bytearray()
    for x in byteArray:
        if isprint(x):
            array.append(x)
        else:
            array.append(0x2E)
        array.append(0x20)
    return array.decode('utf-8')

# parse a binary data chunk
def parse(
    byteArray
):

    hdr = bytearray([0x80, 0x07, 0x00, 0x2f, 0xa8, 0x00, 0x08, 0x46])
    for i in range(0, len(hdr)):
        a = hdr[i]
        b = byteArray[i]
        if (a!=b) and (0!=i) and (1!=i):
            print('expected hdr is ', binascii.hexlify(hdr))
            print('  actual hdr is ', binascii.hexlify(byteArray))
            raise Exception('mmmh, wrong header')

    hdrType = byteArray[0:2]
    if (0x80==hdrType[0]) and (0x00==hdrType[1]):
        # TODO
        pass
    elif (0x80==hdrType[0]) and (0x01==hdrType[1]):
        # TODO
        pass
    elif (0x80==hdrType[0]) and (0x02==hdrType[1]):
        # model type (I'm too lazy to properly decode value also, don't care about it)
        print("model + type is: F888888 HeatPump");
        return True
    elif (0x80==hdrType[0]) and (0x03==hdrType[1]):
        # box name
        sz = byteArray[9]
        name = byteArray[11:11+sz]
        print('box name is "%s"' % name.decode('utf-8'))
        return True
    elif (0x80==hdrType[0]) and (0x04==hdrType[1]):
        # box id + box code
        sz0 = byteArray[8]
        uuid = byteArray[9:9+sz0]
        sz1 = byteArray[29]
        code = byteArray[30:30+sz1]
        print(
            'box uuid="%s" code="%s"' % (
                uuid.decode('utf-8'),
                code.decode('utf-8'),
            )
        )
        return True
    elif (0x80==hdrType[0]) and (0x05==hdrType[1]):
        # wifi SSID to connect to
        sz = byteArray[9]
        ssid = byteArray[11:11+sz]
        print('WIFI SSID to connect to is "%s"' % ssid.decode('utf-8'))
        return True
    elif (0x80==hdrType[0]) and (0x06==hdrType[1]):
        # password for SSID to connect to
        sz = byteArray[9]
        passwd = byteArray[11:11+sz]
        print('WIFI PASSWD to connect with is "%s"' % passwd.decode('utf-8'))
        return True
    elif (0x80==hdrType[0]) and (0x07==hdrType[1]):
        # password plus a whole bunch of shite - skip
        return True
    elif (0xd0==hdrType[0]) and (0x00==hdrType[1]):
        # TODO
        # this changes A LOT over time, but don't need it
        return True
    elif (0xd0==hdrType[0]) and (0x01==hdrType[1]):

        # this one's got current time (incorrect) and temps sure in it

        hour = byteArray[25]
        minute = byteArray[26]

        # temp is encoded as : temp = (0.5*byteValue - 30.0)
        tIn = byteArray[9]
        tIn *=  0.5
        tIn -= 30.0

        # temp is encoded as : temp = (0.5*byteValue - 30.0)
        tOut = byteArray[10]
        tOut *=  0.5
        tOut -= 30.0

        # seems to be 0 (ON) or 25 (OFF) ... or maybe the other way round
        pumpState = byteArray[14]

        # dump what we found
        print('TIME, 24H MODE: %02dH:%02dM' % (hour, minute))
        print('TEMP OUTPUT: %.2f' % tOut)
        print('TEMP INPUT: %.2f' % tIn)
        print('PUMP STATE: %d' % pumpState)
        print("/bin/bash ./influxwrite.sh 'HPUMP_WIFI' 'tIn' '%.2f'" % tIn)
        print("/bin/bash ./influxwrite.sh 'HPUMP_WIFI' 'tOut' '%.2f'" % tOut)
        print("/bin/bash ./influxwrite.sh 'HPUMP_WIFI' 'state' '%.2f'" % pumpState)
        return True

    elif (0xd0==hdrType[0]) and (0x02==hdrType[1]):
        # this one never seems to change -> boring
        return True
    else:
        # unknown
        raise Exception('unknown type in hdr')

    return True

def doFile(
    fileName
):
    print('==================================================== %s' % fileName)
    with open(fileName, "rb") as f:
        prev = None
        byteArray = f.read()
        marker = bytearray([0xaa, 0x5a, 0xb1])
        markerLen = len(marker)
        while 0<len(byteArray):
            off = byteArray.find(marker)
            if off<0:
                break

            ok = False
            bytesHead = byteArray[:off]
            if prev is not None:
                ok = parse(bytesHead)
            prev = bytesHead

            if False:
                if False==ok:
                    hx = binascii.hexlify(bytesHead)
                    hx = str(hx)[2:-2]
                    xx = ''
                    for j in range(0, 4):
                        for i in range(0, 10):
                            xx += str(i)
                            xx += ' '
                    print(xx)
                    print(hx)
                    print(quoted(bytesHead))
                    print(decimal(bytesHead))
            byteArray = byteArray[(off + markerLen):]

doFile('./raw.bin')

