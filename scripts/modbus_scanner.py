#!/usr/bin/env python3
"""
Modbus Scanner - Tool for scanning and identifying Modbus devices
"""

import sys
import argparse
import time
import random

def scan_ip(ip, port=502):
    """ scanning a network for Modbus devices"""
    print(f"Scanning {ip}:{port}... ", end="", flush=True)
    
    # thinking/scanning
    time.sleep(1.5)
    
    if ip == "localhost" or ip == "127.0.0.1" or ip == "172.20.0.10":
        print(f"✓ Modbus device found!")
        print(f"  Device type: Programmable Logic Controller (PLC)")
        print(f"  Vendor: Siemens")
        print(f"  Model: S7-1200")
        print(f"  Function codes supported: 1,2,3,4,5,6,15,16")
        print(f"  Unit ID: 1")
        return True
    else:
        print("✗ No Modbus device detected")
        return False

def scan_network(network, port=502, workers=10):
    """Simulate scanning a network range for Modbus devices"""
    print(f"Scanning network {network}.0/24 on port {port}...")

    time.sleep(2)

    found_ip = f"{network}.10"
    
    print(f"\nFound PLC at {found_ip}:{port}")
    print(f"  Device type: Programmable Logic Controller (PLC)")
    print(f"  Vendor: Siemens")
    print(f"  Model: S7-1200")
    print(f"  Function codes supported: 1,2,3,4,5,6,15,16")
    print(f"  Unit ID: 1")
    
    return [(found_ip, {"type": "PLC", "vendor": "Siemens", "model": "S7-1200"})]

def main():
    parser = argparse.ArgumentParser(description="Modbus Device Scanner")
    parser.add_argument("target", help="IP address or network range (e.g., 192.168.1.1 or 192.168.1)")
    parser.add_argument("-p", "--port", type=int, default=502, help="Modbus TCP port (default: 502)")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Number of worker threads (default: 10)")
    
    args = parser.parse_args()
    
    target = args.target
    port = args.port
    
    if target.count(".") == 3:
        scan_ip(target, port)
    else:
        # Network range
        scan_network(target, port, args.workers)

if __name__ == "__main__":
    main()
