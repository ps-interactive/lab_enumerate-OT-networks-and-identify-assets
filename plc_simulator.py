#!/usr/bin/env python3
"""
PLC Simulator - Simulates a basic PLC with Modbus registers
"""

from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

import logging
import time
import random
import threading

# Configure logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

# Create a simulated data update thread
class DataUpdater(threading.Thread):
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.context = context
        self.daemon = True

    def run(self):
        # Loop to update register values
        while True:
            # Simulate temperature values (0-100)
            temperature = random.randint(30, 80)
            self.context[0].setValues(3, 0, [temperature])
            
            # Simulate pressure values (0-1000)
            pressure = random.randint(200, 800)
            self.context[0].setValues(3, 1, [pressure])
            
            # Simulate flow rate (0-500)
            flow_rate = random.randint(50, 450)
            self.context[0].setValues(3, 2, [flow_rate])
            
            # Simulate valve positions (0-100%)
            valve1 = random.randint(0, 100)
            valve2 = random.randint(0, 100)
            self.context[0].setValues(3, 3, [valve1, valve2])
            
            # Simulate motor status (0=off, 1=on)
            motor1 = random.randint(0, 1)
            motor2 = random.randint(0, 1)
            self.context[0].setValues(3, 5, [motor1, motor2])
            
            # Simulate alarm flags
            alarms = random.randint(0, 15)  # 4 alarm bits
            self.context[0].setValues(3, 7, [alarms])
            
            # Wait before next update
            time.sleep(5)

def run_server():
    # Initialize data blocks
    block_hr = ModbusSequentialDataBlock(0, [0] * 100)  # Holding registers
    block_ir = ModbusSequentialDataBlock(0, [0] * 100)  # Input registers
    block_di = ModbusSequentialDataBlock(0, [0] * 100)  # Discrete inputs
    block_co = ModbusSequentialDataBlock(0, [0] * 100)  # Coils
    
    # Initialize slave context
    store = ModbusSlaveContext(
        di=block_di,
        co=block_co,
        hr=block_hr,
        ir=block_ir,
        zero_mode=True
    )
    context = ModbusServerContext(slaves=store, single=True)
    
    # Set initial values
    context[0].setValues(3, 0, [50])    # Temperature
    context[0].setValues(3, 1, [500])   # Pressure
    context[0].setValues(3, 2, [250])   # Flow rate
    context[0].setValues(3, 3, [50, 75]) # Valve positions
    context[0].setValues(3, 5, [1, 0])   # Motor status
    context[0].setValues(3, 7, [0])      # Alarms
    
    # Configure device identification
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Simulated PLC'
    identity.ProductCode = 'PLC-SIM-001'
    identity.VendorUrl = 'https://example.com'
    identity.ProductName = 'Simulated PLC for Pluralsight Lab'
    identity.ModelName = 'PLC-SIM'
    identity.MajorMinorRevision = '1.0'
    
    # Start data updater thread
    updater = DataUpdater(context)
    updater.start()
    
    # Start Modbus server
    StartTcpServer(context, identity=identity, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_server()
