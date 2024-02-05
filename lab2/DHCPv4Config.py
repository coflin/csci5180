#!/usr/bin/python

from concurrent.futures import ThreadPoolExecutor
from loguru import logger 
from netmiko import ConnectHandler

def connect_router(ios,router):

    try:
        net_connect = ConnectHandler(**ios)
        logger.info(f"Successfully connected to {router} as {ios['username']}")

        config_router(net_connect,router)

    except Exception as e:
        logger.error(f"Unable to connect to {router} as {ios['username']}: {e}")
        

def config_router(net_connect,router):
    try:
        commands = [
            "int Fa0/1",
            "no shutdown",
            "ip address dhcp",
            "end"
            "write memory"
        ]

        output = net_connect.send_config_set(commands)
        logger.info(f"Configured {router}:Fa0/1 to DHCP")

        print("\n show running-config interface Fa0/1")
        print(net_connect.send_command("show running-config interface Fa0/1"))

    except Exception as e:
        logger.error(f"Unable to set {router}:Fa0/1 to DHCP: {e}")

def main():
    routers = ["10.0.0.3", "10.0.0.4","10.0.0.5"]
    futures = []

    with ThreadPoolExecutor(max_workers=len(routers)) as executor:

        for router in routers:
            ios = {
                "device_type":"cisco_ios",
                "ip":router,
                "username":"snir8112",
                "password":"roomtoor",
            }

            future = executor.submit(connect_router, ios, router)
            futures.append(future)    
        
        for future in futures:
            future.result()



if __name__ == "__main__":
    main()
