#!/usr/bin/python3

from netmiko import ConnectHandler
from pythonping import ping
from loguru import logger
import subprocess
import time
import re
from concurrent.futures import ThreadPoolExecutor


def get_config(net_connect, router):

    ip_interface_brief = net_connect.send_command("show ip interface brief")
    time.sleep(3)
    ospf_neighbors = net_connect.send_command("show ip ospf neighbor")

    print(f"\n\nInterface Details for {router}:\n\n{ip_interface_brief}\n")
    print(f"\n\nOSPF Neighborship for {router}:\n {ospf_neighbors}\n")

    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ip_addresses = re.findall(ip_pattern, ip_interface_brief)

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(check_ping, ip_addresses)


def check_ping(ip_address):
    try:
        result = subprocess.run(['ping', '-c', '5', '-W', '2', ip_address], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            logger.success(f"Ping to {ip_address} successful.")
        else:
            logger.warning(f"Ping to {ip_address} failed.")

    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout while pinging {ip_address}")

    except Exception as e:
        logger.error(f"Error while pinging {ip_address}: {e}")


def main():
    try:
        result = subprocess.run(['ls', '/home/student/git/csci5180/lab7/cfgs'], stdout=subprocess.PIPE)
    
    except Exception as e:
        print(f"Unable to find cfgs/ directory: {e}")

    config_files = result.stdout.decode('utf-8').splitlines()

    for file in config_files:
        router = file.split('.txt')[0]
        ios = {
        "device_type":"cisco_ios",
        "ip":router,
        "username":"snir8112",
        "password":"roomtoor"
        }

        try:
            net_connect = ConnectHandler(**ios)
            print("\n-----------------------------------------------------------------------\n")
            logger.info(f"Connected to {router}")

            with open(f"cfgs/{file}","r") as config_file:
                line = [ line.strip() for line in config_file.readlines() ]
                line = list(filter(None, line))
            
                net_connect.send_config_set(line)
                
                get_config(net_connect, router)
                

        except Exception as e:
            logger.critical(f"Unable to configure on {router}: {e}")

if __name__ == "__main__":
    main()
