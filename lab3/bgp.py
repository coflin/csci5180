#!/usr/bin/python3

try:
    import concurrent.futures 
    from netmiko import ConnectHandler
    from loguru import logger
    from sshInfo import sshInfo

except ModuleNotFoundError:
    print("Please run 'pip3 install loguru netmiko' before running this code")

def connectRouter(ios):
    try:
        net_connect = ConnectHandler(**ios)
        logger.info(f"Successfully connected to {ios['ip']} as {ios['username']}")
    
    except Exception as e:
        logger.error(f"Unable to connect to {ios['ip']} as {ios['username']}. Check config and try again.")

def main():

    credential = sshInfo()

    for i in range(1,3):
        ios = {
            "device_type":"cisco_ios",
            "ip":credential[f'R{i}'],
            "username":credential['Username'],
            "password":credential['Password'],
        }

        connectRouter(ios)

if __name__ == "__main__":
    main()