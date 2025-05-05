#!/usr/bin/env python3
"""
DNP3 Scanner - Tool for scanning and identifying DNP3 devices
"""

import sys
import socket
import struct
import argparse
from concurrent.futures import ThreadPoolExecutor

def create_dnp3_request():
    """Create a DNP3 request packet (link layer message)"""
    # DNP3 header (0x0564)
    header = bytes([0x05, 0x64])
    
    # Length field (5 bytes for header + CRC)
    length = bytes([0x05])
    
    # Control field (reset link states)
    control = bytes([0x00])
    
    # Destination address (broadcast)
    dest = bytes([0xFF, 0xFF])
    
    # Source address (master station 1)
    source = bytes([0x01, 0x00])
    
    # CRC (simplified for this example - real implementation would calculate this)
    crc = bytes([0xA5, 0xA5])
    
    return header + length + control + dest + source + crc

def test_dnp3_device(ip, port=20000, timeout=1):
    """Test if a device speaks DNP3 protocol"""
    try:
        # Create socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        # Create and send DNP3 request
        request = create_dnp3_request()
        sock.send(request)
        
        # Receive response
        response = sock.recv(1024)
        sock.close()
        
        # Basic check for DNP3 response (starts with 0x0564)
        if len(response) >= 2 and response[0] == 0x05 and response[1] == 0x64:
            return True, "Valid DNP3 response received"
        else:
            return False, "Response doesn't match DNP3 protocol"
            
    except Exception as e:
        return False, str(e)

def scan_ip(ip, port=20000):
    """Scan a single IP address for DNP3 devices"""
    print(f"Scanning {ip}:{port}... ", end="", flush=True)
    success, result = test_dnp3_device(ip, port)
    
    if success:
        print(f"✓ DNP3 device found!")
        print(f"  Details: {result}")
    else:
        if "Connection refused" in result:
            print("✗ Port closed")
        elif "timed out" in result:
            print("✗ No response (timed out)")
        else:
            print(f"✗ No DNP3 device detected ({result})")
    
    return success, result

def scan_network(network, port=20000, workers=10):
    """Scan a network range for DNP3 devices"""
    ips = [f"{network}.{i}" for i in range(1, 255)]
    found_devices = []
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for ip in ips:
            success, result = scan_ip(ip, port)
            if success:
                found_devices.append((ip, result))
    
    return found_devices

def main():
    parser = argparse.ArgumentParser(description="DNP3 Device Scanner")
    parser.add_argument("target", help="IP address or network range (e.g., 192.168.1.1 or 192.168.1)")
    parser.add_argument("-p", "--port", type=int, default=20000, help="DNP3 TCP port (default: 20000)")
    parser.add_argument("-w", "--workers", type=int, default=10, help="Number of worker threads (default: 10)")
    
    args = parser.parse_args()
    
    target = args.target
    port = args.port
    
    if target.count(".") == 3:
        # Single IP
        scan_ip(target, port)
    else:
        # Network range
        print(f"Scanning network {target}.0/24 on port {port}...")
        found_devices = scan_network(target, port, args.workers)
        
        print("\nScan complete!")
        print(f"Found {len(found_devices)} DNP3 devices:")
        for i, (ip, result) in enumerate(found_devices, 1):
            print(f"{i}. {ip}:{port}")

if __name__ == "__main__":
    main()
