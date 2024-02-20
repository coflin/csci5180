#!/usr/bin/python3

from datetime import datetime
from napalm import get_network_driver
from sshInfo import sshInfo
import concurrent.futures

def get_running_config(hostname, device_type, device_ip, device_username, device_password):
    driver = get_network_driver(device_type)
    device = driver(hostname=device_ip, username=device_username, password=device_password)
    device.open()
    
    config = device.get_config(retrieve="running")

    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    filename = f"{hostname}_{current_datetime}.txt"

    with open(filename, "w") as file:
        file.write(config['running'])
    
    device.close()

    return filename

def getRunningConfig():
    credentials = sshInfo()

    files = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for hostname, info in credentials.items():
            device_type = info["Device_Type"]
            device_ip = info["IP"]
            device_username = info["Username"]
            device_password = info["Password"]

            future = executor.submit(get_running_config, hostname, device_type, device_ip, device_username, device_password)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            files.append(future.result())

    return files  

if __name__ == "__main__":
    getRunningConfig()