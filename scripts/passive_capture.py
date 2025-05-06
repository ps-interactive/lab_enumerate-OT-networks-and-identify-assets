#!/usr/bin/env python3
"""
Passive Network Capture Tool - For detecting OT protocol traffic without active scanning
"""

import sys
import time
import signal
import argparse
import random

# Global variables for statistics
packets_captured = 0
ot_packets_captured = 0
devices_seen = {}
protocols_seen = {}

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n--- Capture Summary ---")
    print(f"Total packets captured: {packets_captured}")
    print(f"OT protocol packets: {ot_packets_captured}")
    
    print("\nDevices detected:")
    for device, details in devices_seen.items():
        print(f"  {device}:")
        for proto, count in details.items():
            print(f"    {proto}: {count} packets")
    
    print("\nProtocols detected:")
    for proto, count in protocols_seen.items():
        print(f"  {proto}: {count} packets")
    
    print("\nKey findings:")
    print("  - Hidden RTU discovered at 172.20.0.40 using DNP3 protocol")
    print("  - This device wasn't found by active scanning because it's protected by firewall rules")
    print("  - The RTU appears to be communicating with the Engineering Workstation periodically")
    print("  - The firewall is configured to only allow specific source IPs to communicate with the RTU")
    
    sys.exit(0)

def simulate_capture(interface, timeout=0):
    """Simulate packet capture and display results"""
    global packets_captured, ot_packets_captured, devices_seen, protocols_seen
    
    print(f"Starting passive capture on interface {interface}")
    print("Looking for OT protocol traffic (Modbus, DNP3, EtherNet/IP, etc.)")
    print("Press Ctrl+C to stop and view summary")
    print("")
    
    # Add PLC to seen devices
    if "172.20.0.10" not in devices_seen:
        devices_seen["172.20.0.10"] = {}
    if "Modbus TCP" not in devices_seen["172.20.0.10"]:
        devices_seen["172.20.0.10"]["Modbus TCP"] = 0
    
    # Add HMI to seen devices
    if "172.20.0.20" not in devices_seen:
        devices_seen["172.20.0.20"] = {}
    if "HTTP" not in devices_seen["172.20.0.20"]:
        devices_seen["172.20.0.20"]["HTTP"] = 0
    
    # Add Engineering Workstation to seen devices
    if "172.20.0.30" not in devices_seen:
        devices_seen["172.20.0.30"] = {}
    if "HTTP" not in devices_seen["172.20.0.30"]:
        devices_seen["172.20.0.30"]["HTTP"] = 0
    
    # Add hidden RTU to seen devices
    if "172.20.0.40" not in devices_seen:
        devices_seen["172.20.0.40"] = {}
    if "DNP3" not in devices_seen["172.20.0.40"]:
        devices_seen["172.20.0.40"]["DNP3"] = 0
    
    # Add protocols
    protocols_seen["Modbus TCP"] = 0
    protocols_seen["HTTP"] = 0
    protocols_seen["DNP3"] = 0
    
    # Simulate packet display
    start_time = time.time()
    last_print = start_time
    
    try:
        while timeout == 0 or time.time() - start_time < timeout:
            current_time = time.time()
            
            # Only print new packet info every 2-3 seconds
            if current_time - last_print >= random.uniform(2, 3):
                last_print = current_time
                
                # Randomly choose which kind of packet to display
                packet_type = random.choice(["modbus", "http", "http", "dnp3"])
                
                if packet_type == "modbus":
                    # Modbus TCP traffic
                    src_ip = "172.20.0.10"
                    dst_ip = "172.20.0.20"
                    protocol = "Modbus TCP"
                    payload = "00010000000601030001000A"
                    
                    print(f"[{time.strftime('%H:%M:%S')}] {protocol} traffic: {src_ip} -> {dst_ip}")
                    print(f"  Payload length: 12 bytes")
                    print(f"  First few bytes: {payload}")
                    print("")
                    
                    # Update stats
                    packets_captured += 1
                    ot_packets_captured += 1
                    devices_seen[src_ip][protocol] = devices_seen[src_ip].get(protocol, 0) + 1
                    protocols_seen[protocol] = protocols_seen.get(protocol, 0) + 1
                    
                elif packet_type == "http":
                    # HTTP traffic for HMI or Engineering Workstation
                    src_ip = random.choice(["172.20.0.20", "172.20.0.30"])
                    dst_ip = "172.20.0.10"
                    protocol = "HTTP"
                    payload = "474554202f20485454"
                    
                    print(f"[{time.strftime('%H:%M:%S')}] {protocol} traffic: {src_ip} -> {dst_ip}")
                    print(f"  Payload length: 9 bytes")
                    print(f"  First few bytes: {payload}")
                    print("")
                    
                    # Update stats
                    packets_captured += 1
                    devices_seen[src_ip][protocol] = devices_seen[src_ip].get(protocol, 0) + 1
                    protocols_seen[protocol] = protocols_seen.get(protocol, 0) + 1
                    
                elif packet_type == "dnp3":
                    # DNP3 traffic - HIDDEN DEVICE!
                    src_ip = "172.20.0.40"
                    dst_ip = "172.20.0.30"
                    protocol = "DNP3"
                    payload = "0564050000ffff0100a5a5"
                    
                    print(f"[{time.strftime('%H:%M:%S')}] {protocol} traffic: {src_ip} -> {dst_ip}")
                    print(f"  Payload length: 12 bytes")
                    print(f"  First few bytes: {payload}")
                    print("")
                    
                    # Update stats
                    packets_captured += 1
                    ot_packets_captured += 1
                    if src_ip not in devices_seen:
                        devices_seen[src_ip] = {}
                    devices_seen[src_ip][protocol] = devices_seen[src_ip].get(protocol, 0) + 1
                    protocols_seen[protocol] = protocols_seen.get(protocol, 0) + 1
                
                # Sleep a bit to simulate real packet intervals
                time.sleep(random.uniform(0.1, 0.3))
    
    except KeyboardInterrupt:
        # Will be caught by signal handler
        pass

def main():
    parser = argparse.ArgumentParser(description="Passive OT Network Traffic Analyzer")
    parser.add_argument("-i", "--interface", default="eth0", help="Network interface to sniff on")
    parser.add_argument("-t", "--timeout", type=int, default=0, help="Capture timeout in seconds (0 = unlimited)")
    
    args = parser.parse_args()
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start simulated capture
    simulate_capture(args.interface, args.timeout)
    
    # If we get here due to timeout, show summary
    signal_handler(None, None)

if __name__ == "__main__":
    main()
