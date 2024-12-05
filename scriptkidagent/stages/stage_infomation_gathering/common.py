import subprocess
import os
from typing import Dict, List


def is_root():
    return os.geteuid() == 0


def scan_ip_segment(ip_segment: str) -> Dict[str, Dict[str, List[int]]]:
    """
    Scans the given IP segment using nmap to find all online hosts and their open ports for all protocols.

    Args:
        ip_segment (str): The IP segment to scan, e.g., '192.168.1.0/24'.

    Returns:
        Dict[str, Dict[str, List[int]]]: A dictionary where keys are IP addresses, and values are dictionaries
        with protocol names as keys and lists of open ports as values.
    """
    try:
        print(f"Scanning IP segment: {ip_segment} for all protocols...")
        # Run the nmap command for TCP, UDP, and other protocols
        if is_root():
            result = subprocess.run(
                ['nmap', '-sS', '-T4', '-n', '-oX', '-', ip_segment],
                # ['nmap', '-sS',  '-P', '1-10000',  ip_segment],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            print("Warning: Running nmap as a non-root user. Some scans may not work.")
            result = subprocess.run(
                ['nmap', '-sT', '-T4', '-n', '-oX', '-', ip_segment],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

        if result.returncode != 0:
            print(f"Error during nmap scan: {result.stderr}")
            return {}

        # Parse nmap output
        return parse_nmap_output(result.stdout)

    except FileNotFoundError:
        print("Error: nmap is not installed or not in PATH. Please install it to use this script.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}


def parse_nmap_output(output: str) -> Dict[str, Dict[str, List[int]]]:
    """
    Parses the nmap output and returns a dictionary of results.

    Args:
        output (str): XML output from nmap.

    Returns:
        Dict[str, Dict[str, List[int]]]: A dictionary where keys are IP addresses, and values are dictionaries
        with protocol names as keys and lists of open ports as values.
    """
    import xml.etree.ElementTree as ET

    results = {}

    try:
        root = ET.fromstring(output)
        for host in root.findall('host'):
            # Get host's IP address
            address = host.find('address')
            if address is not None:
                ip = address.get('addr')
                # Initialize an empty protocol dictionary for this IP
                results[ip] = {}

            # Get open ports
            ports = host.find('ports')
            if ports is not None and ip:
                for port in ports.findall('port'):
                    protocol = port.get('protocol')  # e.g., 'tcp', 'udp'
                    port_id = port.get('portid')
                    state = port.find('state').get('state')
                    if state == 'open':
                        # Add the open port to the protocol list
                        results[ip].setdefault(protocol, []).append(int(port_id))

    except ET.ParseError as e:
        print(f"Error parsing nmap output: {e}")

    return results
