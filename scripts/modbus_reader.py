#!/usr/bin/env python3
"""
Modbus Reader - Tool for reading registers from Modbus devices
"""

import sys
import argparse
import time
import random

def read_holding_registers(ip, port=502, unit=1, address=0, count=10):
    """Simulate reading holding registers from a Modbus device"""
    print(f"Connecting to Modbus PLC at {ip}:{port}...")
    
    #  connection time
    time.sleep(1)
    
    print("Connection successful!")
    print(f"Reading {count} holding registers starting at address {address} from unit {unit}...")
    
    #  reading time
    time.sleep(1.5)
    
    #  register values for a typical industrial process
    registers = [
        56,    # Temperature value (°C)
        478,   # Pressure value (kPa)
        242,   # Flow rate (L/min)
        63,    # Valve 1 position (%)
        81,    # Valve 2 position (%)
        1,     # Motor 1 status (1=on, 0=off)
        0,     # Motor 2 status (1=on, 0=off)
        2,     # Alarm flags
        125,   # Setpoint temperature
        350    # Setpoint pressure
    ]
    
    # Print register values with descriptions
    print("\nRegister Values:")
    descriptions = [
        "Temperature value (°C)",
        "Pressure value (kPa)",
        "Flow rate (L/min)",
        "Valve 1 position (%)",
        "Valve 2 position (%)",
        "Motor 1 status (1=on, 0=off)",
        "Motor 2 status (1=on, 0=off)",
        "Alarm flags",
        "Setpoint temperature (°C)",
        "Setpoint pressure (kPa)"
    ]
    
    for i in range(min(count, len(registers))):
        reg_address = address + i
        value = registers[i]
        desc = descriptions[i] if i < len(descriptions) else ""
        print(f"  Register {reg_address}: {value} - {desc}")
    
    print("\nAnalysis:")
    print("  This PLC appears to be controlling a process with:")
    print("  - Temperature monitoring and control")
    print("  - Pressure regulation")
    print("  - Flow monitoring")
    print("  - Dual valve positioning")
    print("  - Two motor controls")
    print("  - Alarm system active (value 2 indicates warnings present)")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Modbus Register Reader")
    parser.add_argument("host", help="IP address of the Modbus device")
    parser.add_argument("-p", "--port", type=int, default=502, help="Modbus TCP port (default: 502)")
    parser.add_argument("-u", "--unit", type=int, default=1, help="Unit ID (default: 1)")
    parser.add_argument("-a", "--address", type=int, default=0, help="Starting address (default: 0)")
    parser.add_argument("-c", "--count", type=int, default=10, help="Number of registers to read (default: 10)")
    
    args = parser.parse_args()
    
    read_holding_registers(args.host, args.port, args.unit, args.address, args.count)

if __name__ == "__main__":
    main()
