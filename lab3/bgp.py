#!/usr/bin/python3

"""
Lab 3: The code does the following
1. Connects to the routers and checks if the connection is established
2. Configures iBGP on the routers based on bgp.conf file
3. Updates bgp.conf file with the BGP neighbor state
4. Displays all the BGP Neighbors
5. Displays all routes learnt via BGP
"""


try:
    import concurrent.futures
    from ipaddress import IPv4Network
    import json
    from loguru import logger
    from netmiko import ConnectHandler
    import os
    from prettytable import PrettyTable
    from sshInfo import sshInfo
    import sys

except ModuleNotFoundError:
    print("Please run 'pip3 install loguru netmiko' before running this code")

"""
- Connects to the router
- Parameters: ios (dict), hostname (str)
- Returns: net_connect (obj), hostname (str)
"""
def connectRouter(ios,hostname):

    try:
        net_connect = ConnectHandler(**ios)
        logger.info(f"Successfully connected to {ios['ip']} as {ios['username']}")
        return net_connect
    
    except Exception as e:
        logger.error(f"Unable to connect to {ios['ip']} as {ios['username']}. Check config and try again: {e}")
        sys.exit()

"""
- Configures iBGP on the routers based on bgp.conf file
- Parameters: net_connect (obj), hostname (str)
- Returns: bgpconf (dict)

 -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
Configuring iBGP example:
router bgp 100
 neighbor 198.51.100.3 remote-as 100
 neighbor 198.51.100.3 update-source FastEthernet0/0
 neighbor 198.51.100.3 soft-reconfiguration rebound
 network 10.10.10.1 mask 255.255.255.255
 network 11.11.11.1 mask 255.255.255.255
 -------------------

 In [22]: print(IPv4Network("10.10.10.1/32").netmask)
 Out: 255.255.255.255

 In [23]: print(IPv4Network("10.10.10.1/32").network_address)
 Out: 10.10.10.1
 -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
"""
def configBGP(net_connect,hostname):
    
    try:
        with open("bgp.conf","r") as file:
            bgpconfig = [line for line in file]
            bgpconf = json.loads(bgpconfig[0])['Routers'][hostname]
    
    except FileNotFoundError:
        logger.error("bgp.conf file not found. Please check if the file exists and is in the same location as this script.")
        sys.exit()

    except json.decoder.JSONDecodeError as e:
        logger.error(f"Please ensure bgp.conf file is enclosed in double quotes (\"\") and not single quotes (\'\') : {e}")

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

        """
        Commands validation
        """

        for line in range(len(device_output)):
            if "%" in device_output[line]:
                logger.error(f"Invalid/Incomplete command: {(device_output[line-2])}\n{(device_output[line-1])}")
                sys.exit()
    
        logger.info(f"Configured iBGP on {hostname}")

        return bgpconf

    except Exception as e:
        logger.error(f"Unable to configure iBGP on {hostname}: {e}")


"""
Updates BGP State:
- Updates bgp.conf file with the BGP neighbor state
- Parameters: net_connect (obj), hostname (str), bgpconf (dict)
- Returns: bgpconf (dict)
"""
def updateBGPState(net_connect, hostname, bgpconf):

    output = net_connect.send_command(f"show ip bgp neighbors {bgpconf['neighbor_ip']} | include BGP state = ")

    if output:
        bgpstate = output.replace(",", "").split()[3]
        bgpconf['BGP State'] = bgpstate

        return bgpconf

    else:
        logger.error(f"BGP peer {bgpconf['neighbor_ip']} does not exist. Check and try again.")


"""
Shows BGP Neighbors:
- Displays all the BGP Neighbors
- Parameters: net_connect (obj), hostname (str)
- Returns: None
"""
def showBGPNeighbors(net_connect,hostname):
    bgp_status = net_connect.send_command("show ip bgp neighbors | include BGP state | neighbor is")
    bgp_neighbor_ip = bgp_status.replace(",","").split()[3]
    bgp_neighbor_as = bgp_status.replace(",","").split()[6]
    bgp_neighbor_status = bgp_status.replace(",","").split()[12]

    bgp_neighbors_table = PrettyTable(["BGP Neighbor IP","BGP Neighbor AS","BGP Neighbor State"])
    bgp_neighbors_table.add_row([bgp_neighbor_ip,bgp_neighbor_as,bgp_neighbor_status])

    print(f"{hostname} BGP Neighbors Table\n{bgp_neighbors_table}\n\n")


"""
Shows BGP Routes:
- Displays all routes learnt via BGP
- Parameters: net_connect (obj), neighbor_ip (str), hostname (str)
- Returns: None
"""
def showBGPRoutes(net_connect,neighbor_ip,hostname):

    bgp_routes_table = PrettyTable(["Received Routes"])

    bgp_routes = net_connect.send_command(f"show ip bgp neighbors {neighbor_ip} received-routes | include \*>")
    for bgp_route in bgp_routes.split("\n"):
        bgp_routes_table.add_row([bgp_route.replace("*>i","").split()[0]])
    
    print(f"{hostname} BGP received routes\n{bgp_routes_table}\n\n")


"""
Saves Config:
- Saves the router's running-config to a file
- Parameters: net_connect (obj), hostname (str)
- Returns: None
"""
def saveConfig(net_connect,hostname):
    with open (f"{hostname}_config.txt","w") as file:
        output = net_connect.send_command("show running-config",read_timeout = 20)
        file.write(output)
        logger.info(f"Saved {hostname}'s running-config as {hostname}_config.txt")


"""
Main function
- Connects to the routers, configures iBGP, updates BGP state, displays BGP neighbors and routes, and saves router config
- Parameters: None
- Returns: None
"""
def main():

    credential = sshInfo()

    net_connect_dict = {}
    new_bgp_config  = {"Routers":{}}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(1,3):
            hostname = f'R{i}'
            ios = {
                "device_type":'cisco_ios',
                "ip":f"{credential[hostname]}",
                "username":f"{credential['Username']}",
                "password":f"{credential['Password']}"
            }

            net_connect = executor.map(connectRouter, [ios], [hostname])

            for nc in net_connect:
                net_connect_dict[hostname] = nc

            bgpconfig = executor.map(configBGP, [net_connect_dict[hostname]], [hostname])

            for bgpconf in bgpconfig:
                newbgpconf = updateBGPState(net_connect_dict[hostname], hostname, bgpconf)
                new_bgp_config["Routers"][hostname] = newbgpconf

            showBGPNeighbors(net_connect_dict[hostname],hostname)
            showBGPRoutes(net_connect_dict[hostname],new_bgp_config["Routers"][hostname]["neighbor_ip"],hostname)
            saveConfig(net_connect_dict[hostname],hostname)

    with open("bgp_new.conf", "w") as file:
        json.dump(new_bgp_config, file, indent=4)

    logger.info("Updated BGP State information in bgp_new.conf file.")
            
      
if __name__ == "__main__":
    main()