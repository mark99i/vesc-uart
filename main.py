import json

import serial
import time
from conv import *
import uart
import datatypes
import commands
import network

print("starting server")
server = network.ApiServer()
server.start_server("0.0.0.0", 2002)

uart = uart.UART(debug=True)
uart.connect("COM4", 115200)
print("started")

while 1:
    sended = int(time.time() * 1000)

    #res = commands.Commands.COMM_FW_VERSION(uart, 15)
    #res = json.dumps(res, indent=4)
    #print(res)
    print(commands.Commands.get_local_controller_id(uart))

    print("req_time:", int((time.time() * 1000) - sended))

    time.sleep(2)
    break