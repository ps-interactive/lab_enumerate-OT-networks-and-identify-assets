#!/usr/bin/env python3
"""
Modbus Scanner - Tool for scanning and identifying Modbus devices
"""

import sys
import socket
import struct
import argparse
from concurrent.futures import ThreadPoolExecutor

def create_modbus_request(slave_id=1, function_code=4, starting_address=0, quantity=1):
    """Create a Modbus TCP request packet"""
    # Modbus Application Protocol header
    transaction_id = struct.pack(">H", 1)  # Transaction ID
    protocol_id = struct.pack(">H", 0)     # Protocol ID (0 for Modbus TCP)
    length = struct.pack(">H", 6)          # Length of remaining bytes
    unit_id = struct.pack(">B", slave_id)  # Unit ID (slave address)
    
    # Modbus request
    function = struct.pack(">B", function_code)
    address = struct.pack(">H", starting_address)
    count = struct.pack(">H", quantity)
    
    return transaction_id + protocol_id + length + unit_id + function + address + count

def parse_modbus_response(response):
    """Parse a Modbus TCP response packet"""
    if len(response) < 9:
        return "Error: Response too short"
    
    # Parse header
    transaction_id = struct.unpack(">H", response[0:2])[0]
    protocol_id = struct.unpack(">H", response[2:4])[0]
    length = struct.unpack(">H", response[4:6])[0]
    unit_id = struct.unpack(">B", response[6:7])[0]
    function_code = struct.unpack(">B", response[7:8])[0]
    
    # Check if error response
    if function_code > 0x80:
        exception_code = struct.unpack(">B", response[8:9])[0]
        return f"Error: Exception code {exception_code}"
    
    # Handle successful response
    byte_count = struct.unpack(">B", response[8:9])[0]
    data = response[9:9+byte_count]
    
    return {
        "transaction_id": transaction_id,
        "unit_id": unit_id,
        "function_code": function_code,
        "data": data
    }

def test_modbus_device(ip, port=502, timeout=1):
    """Test if a device is a Modbus device"""
    try:
        # Create socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        # Create and send Modbus request for device ID (function code 17/0x11)
        request = create_modbus_request(slave_id=1, function_code=0x11, starting_address=0, quantity=0)
        sock.send(request)
        
        # Receive response
        response = sock.recv(1024)
        sock.close()
        
        # Parse response
        result = parse_modbus_response(response)
        
        if isinstance(result, str) and result.startswith("Error"):
            # Try a different function code if we got an error
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            
            # Try reading holding registers (function code 3)
            request = create_modbus_request(slave_id=1, function_code=3, starting_address=0, quantity=1)
            sock.send(request)
            response = sock.recv(1024)
            sock.close()
            
            result = parse_modbus_response(response)
        
        return True, result
    except Exception as e:
        return False, str(e)

def scan_ip(ip, port=502):
    """Scan a single IP address for Modbus devices"""
    print(f"Scanning {ip}:{port}... ", end="", flush=True)
    success, result = test_modbus_device(ip, port)
    
    if success:
        if isinstance(result, dict):
            print(f"✓ Modbus device found!")
            print(f"  Function code: {result['function_code']}")
            print(f"  Unit ID: {result['unit_id']}")
            if 'data' in result:
                print(f"  Data length: {len(result['data'])} bytes")
        else:
            print(f"✓ Possible Modbus device (responded to connection)")
    else:
        print("✗ No Modbus device detected")
    
    return success, result

def scan_network(network, port=502, workers=10):
    """Scan a network range for Modbus devices"""
    ips = [f"{network}.{i}" for i in range(1, 255)]
    found_devices = []
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for ip in ips:
            success, result = scan_ip(ip, port)
            if success:
                found_devices.append((ip, result))
    
    return found_devices

def main():
    parser = argparse.ArgumentParser(description="Modbus Device Scanner")
    parser.add_argument("target", help="IP address or network range (e.g., 192.168.1.1 or 192.168.1)")
    parser.add_argument("-p", "--port", type=int, default=502, help="Modbus TCP port (default: 502)")
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
        print(f"Found {len(found_devices)} Modbus devices:")
        for i, (ip, result) in enumerate(found_devices, 1):
            print(f"{i}. {ip}:{port}")

if __name__ == "__main__":
    main()
