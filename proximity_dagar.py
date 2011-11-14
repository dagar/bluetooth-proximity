#! /usr/bin/env python
# Daniel Agar
# 2011-11-13

# TODO: add keyboard ctrl c handling
# TODO: add command line arguments
# TODO: add error handling and standard loggin

import fcntl
import struct
import array
import bluetooth
import bluetooth._bluetooth as bt

import time
import os
import datetime

def bluetooth_rssi(addr):
    # Open hci socket
    hci_sock = bt.hci_open_dev()
    hci_fd = hci_sock.fileno()

    # Connect to device (to whatever you like)
    bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    bt_sock.settimeout(10)
    result = bt_sock.connect_ex((addr, 1))	# PSM 1 - Service Discovery

    try:
        # Get ConnInfo
        reqstr = struct.pack("6sB17s", bt.str2ba(addr), bt.ACL_LINK, "\0" * 17)
        request = array.array("c", reqstr )
        handle = fcntl.ioctl(hci_fd, bt.HCIGETCONNINFO, request, 1)
        handle = struct.unpack("8xH14x", request.tostring())[0]

        # Get RSSI
        cmd_pkt=struct.pack('H', handle)
        rssi = bt.hci_send_req(hci_sock, bt.OGF_STATUS_PARAM,
                     bt.OCF_READ_RSSI, bt.EVT_CMD_COMPLETE, 4, cmd_pkt)
        rssi = struct.unpack('b', rssi[3])[0]

        # Close sockets
        bt_sock.close()
        hci_sock.close()

        return rssi

    except:
        return None



far = True
far_count = 0

# assume phone is initially far away
rssi = -255
rssi_prev1 = -255
rssi_prev2 = -255

near_cmd = 'br -n 1'
far_cmd = 'br -f 1'

dagar_addr = '04:18:0F:46:C6:67'
emily_addr = '43:29:B1:55:00:00'

debug = 1

while True:
    # get rssi reading for address
    rssi = bluetooth_rssi(dagar_addr)

    if debug:
        print datetime.datetime.now(), rssi, rssi_prev1, rssi_prev2, far, far_count


    if rssi == rssi_prev1 == rssi_prev2 == None:
        print datetime.datetime.now(), "can't detect address"
        time.sleep(3)

    elif rssi == rssi_prev1 == rssi_prev2 == 0:
        # change state if nearby
        if far:
            far = False
            far_count = 0
            os.system(near_cmd)
            print datetime.datetime.now(), "changing to near"

        time.sleep(30)

    elif rssi < -2 and rssi_prev1 < -2 and rssi_prev2 < -2:
        # if were near and single has been consisitenly low

        # need 10 in a row to set to far
        far_count += 1
        if not far and far_count > 10:
            # switch state to far
            far = True
            far_count = 0
            os.system(far_cmd)
            print datetime.datetime.now(), "changing to far"
            time.sleep(5)

    else:
        far_count = 0


    rssi_prev1 = rssi
    rssi_prev2 = rssi_prev1


