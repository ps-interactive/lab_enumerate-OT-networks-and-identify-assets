#!/usr/bin/env python3
"""
Passive Network Capture Tool - For detecting OT protocol traffic without active scanning
"""

import sys
import time
import signal
import argparse
from scapy.all import sniff, Ether, IP, TCP, UDP, Raw

# OT Protocol port definitions
OT_PROTOCOLS = {
    502: "Modbus TCP",
    20000: "DNP3",
    44818: "EtherNet/IP",
    102: "S7Comm (Siemens)",
    1089: "Foundation Fieldbus HSE",
    1090: "Foundation Fieldbus HSE",
    1091: "Foundation Fieldbus HSE",
    2222: "EtherCAT",
    34962: "PROFINET IO Data",
    34963: "PROFINET IO Control",
    34964: "PROFINET IO",
    47808: "BACnet/IP",
}

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
    
    sys.exit(0)

def identify_ot_protocol(pkt):
    """Identify OT protocol based on port numbers"""
    if not pkt.haslayer(TCP) and not pkt.haslayer(UDP):
        return None
    
    src_port = None
    dst_port = None
    
    if pkt.haslayer(TCP):
        src_port = pkt[TCP].sport
        dst_port = pkt[TCP].dport
    elif pkt.haslayer(UDP):
        src_port = pkt[UDP].sport
        dst_port = pkt[UDP].dport
    
    # Check if either port matches known OT protocols
    if src_port in OT_PROTOCOLS:
        return OT_PROTOCOLS[src_port]
    elif dst_port in OT_PROTOCOLS:
        return OT_PROTOCOLS[dst_port]
    
    return None

def analyze_packet(pkt):
    """Analyze a packet for OT protocol information"""
    global packets_captured, ot_packets_captured, devices_seen, protocols_seen
    
    packets_captured += 1
    
    if not pkt.haslayer(IP):
        return
    
    src_ip = pkt[IP].src
    dst_ip = pkt[IP].dst
    
    # Identify OT protocol
    protocol = identify_ot_protocol(pkt)
    
    if protocol:
        ot_packets_captured += 1
        
        # Add to protocols seen
        if protocol not in protocols_seen:
            protocols_seen[protocol] = 0
        protocols_seen[protocol] += 1
        
        # Add source device
        if src_ip not in devices_seen:
            devices_seen[src_ip] = {}
        if protocol not in devices_seen[src_ip]:
            devices_seen[src_ip][protocol] = 0
        devices_seen[src_ip][protocol] += 1
        
        # Add destination device
        if dst_ip not in devices_seen:
            devices_seen[dst_ip] = {}
        if protocol not in devices_seen[dst_ip]:
            devices_seen[dst_ip][protocol] = 0
        devices_seen[dst_ip][protocol] += 1
        
        # Print detection
        print(f"[{time.strftime('%H:%M:%S')}] {protocol} traffic: {src_ip} -> {dst_ip}")
        
        # Print basic packet info for debugging
        if pkt.haslayer(Raw) and len(pkt[Raw].load) > 0:
            print(f"  Payload length: {len(pkt[Raw].load)} bytes")
            print(f"  First few bytes: {pkt[Raw].load[:10].hex()}")
        
        print("")

def main():
    parser = argparse.ArgumentParser(description="Passive OT Network Traffic Analyzer")
    parser.add_argument("-i", "--interface", default="eth0", help="Network interface to sniff on")
    parser.add_argument("-t", "--timeout", type=int, default=0, help="Capture timeout in seconds (0 = unlimited)")
    
    args = parser.parse_args()
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"Starting passive capture on interface {args.interface}")
    print("Looking for OT protocol traffic (Modbus, DNP3, EtherNet/IP, etc.)")
    print("Press Ctrl+C to stop and view summary")
    print("")
    
    # Start sniffing
    sniff(iface=args.interface, prn=analyze_packet, store=0, timeout=args.timeout)
    
    # If we get here due to timeout, show summary
    signal_handler(None, None)

if __name__ == "__main__":
    main()
