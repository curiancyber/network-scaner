import os
import socket
import subprocess
import threading
from datetime import datetime

# Function to perform a ping sweep to identify live hosts in a subnet
def ping_sweep(network):
    print(f"Starting Ping Sweep on {network}")
    live_hosts = []
    
    for i in range(1, 255):
        ip = f"{network}.{i}"
        response = os.popen(f"ping -c 1 -W 1 {ip}").read()
        if "1 packets transmitted, 1 received" in response:
            live_hosts.append(ip)
            print(f"Host found: {ip}")
    
    return live_hosts

# Function to scan a range of ports on a target IP
def port_scan(ip, start_port, end_port):
    print(f"\nScanning {ip} for open ports between {start_port}-{end_port}...")
    open_ports = []
    
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        
        result = sock.connect_ex((ip, port))  # Connect to port
        
        if result == 0:
            print(f"Port {port} is open.")
            open_ports.append(port)
        sock.close()
    
    return open_ports

# Function to detect services running on open ports
def service_detection(ip, open_ports):
    services = {}
    
    for port in open_ports:
        try:
            # Attempt to retrieve service banner
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, port))
            sock.send(b'Hello\r\n')  # Send a simple request to get a banner
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            services[port] = banner.strip()
            sock.close()
        except:
            services[port] = "Unknown service"
    
    return services

# Function to handle scanning of live hosts and ports concurrently
def network_scan(target_ip, network, start_port, end_port):
    print("\nStarting network scan...\n")
    
    # Ping Sweep
    live_hosts = ping_sweep(network)
    
    # Port Scanning
    open_ports_by_host = {}
    
    for host in live_hosts:
        open_ports = port_scan(host, start_port, end_port)
        if open_ports:
            open_ports_by_host[host] = open_ports
    
    # Service Detection
    service_by_host = {}
    for host, open_ports in open_ports_by_host.items():
        services = service_detection(host, open_ports)
        service_by_host[host] = services
    
    print("\nScan results:")
    for host, services in service_by_host.items():
        print(f"\nHost: {host}")
        for port, service in services.items():
            print(f"  Port {port}: {service}")

# Main function to prompt the user for input and execute the scan
def main():
    print("Network PenTest Tool - Information Gathering and Scanning")
    print(f"Started at: {datetime.now()}")
    
    # Get user input
    network = input("Enter network (e.g., 192.168.1): ")
    start_port = int(input("Enter start port: "))
    end_port = int(input("Enter end port: "))
    target_ip = input("Enter a single IP for detailed port scan (optional): ")
    
    if target_ip:
        print("\nScanning single target IP...\n")
        open_ports = port_scan(target_ip, start_port, end_port)
        services = service_detection(target_ip, open_ports)
        print(f"\nScan results for {target_ip}:")
        for port, service in services.items():
            print(f"  Port {port}: {service}")
    else:
        # Network scan
        network_scan(target_ip, network, start_port, end_port)

if __name__ == '__main__':
    main()
