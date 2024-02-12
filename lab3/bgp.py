#!/usr/bin/python3

try:
    import concurrent.futures
    from ipaddress import IPv4Network
    import json
    from netmiko import ConnectHandler
    from loguru import logger
    from sshInfo import sshInfo
    import sys

except ModuleNotFoundError:
    print("Please run 'pip3 install loguru netmiko' before running this code")


def connectRouter(ios,hostname):

    try:
        net_connect = ConnectHandler(**ios)
        logger.info(f"Successfully connected to {ios['ip']} as {ios['username']}")
    
    except Exception as e:
        logger.error(f"Unable to connect to {ios['ip']} as {ios['username']}. Check config and try again: {e}")
        sys.exit()

    configBGP(net_connect,hostname)

"""
Configuring iBGP:
router bgp 100
 network 10.10.10.1 mask 255.255.255.0
 network 11.11.11.1 mask 255.255.255.0
 neighbor 198.51.100.3 remote-as 100
 neighbor 198.51.100.3 update-source FastEthernet0/0
 -------------------

 In [22]: print(IPv4Network("10.10.10.1/32").netmask)
 Out: 255.255.255.255

 In [23]: print(IPv4Network("10.10.10.1/32").network_address)
 Out: 10.10.10.1
"""

def configBGP(net_connect,hostname):
    
    try:
        with open("bgp.conf","r") as file:
            bgpconf = [line for line in file]
            bgpconf = json.loads(bgpconf[0])['Routers'][hostname]
    
    except FileNotFoundError:
        logger.error("bgp.conf file not found. Please check if the file exists and is in the same location as this script.")
        sys.exit()

    try:
        commands = [
                f"router bgp {bgpconf['local_asn']}",
                f"neighbor {bgpconf['neighbor_ip']} remote-as {bgpconf['neighbor_remote_as']}",
                f"neighbor {bgpconf['neighbor_ip']} update-source {bgpconf['update-source']}",
                f"neighbor {bgpconf['neighbor_ip']} soft-reconfiguration inbound"
            ]

        for network in bgpconf['NetworkListToAdvertise']:
            netaddress = IPv4Network(network).network_address
            netmask = IPv4Network(network).netmask
            commands.append(f"network {netaddress} mask {netmask}")

        output = net_connect.send_config_set(commands)
        device_output = output.splitlines()

        for line in range(len(device_output)):
            if "%" in device_output[line]:
                logger.error(f"Invalid/Incomplete command: {(device_output[line-2])}\n{(device_output[line-1])}")
                sys.exit()
    
        logger.info(f"Configured iBGP on {hostname}")

    except Exception as e:
        logger.error(f"Unable to configure iBGP on {hostname}: {e}")

def main():

    credential = sshInfo()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(1,3):
            hostname = f'R{i}'
            ios = {
                "device_type":'cisco_ios',
                "ip":f"{credential[hostname]}",
                "username":f"{credential['Username']}",
                "password":f"{credential['Password']}"
            }

            executor.map(connectRouter, [ios], [hostname])
            
if __name__ == "__main__":
    main()