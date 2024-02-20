import os
from napalm import get_network_driver
from sshInfo import sshInfo
import concurrent.futures
from difflib import ndiff
import subprocess

def diff_config(hostname, device_type, device_ip, device_username, device_password):
    diff = ""

    driver = get_network_driver(device_type)
    device = {'hostname':device_ip,'username':device_username,'password':device_password}

    with driver(**device) as device:
        running_config = device.get_config(retrieve="running")
    
    result = subprocess.run(f"ls -tr | grep {hostname} | tail -n1", shell=True, stdout=subprocess.PIPE)
    if result.returncode == 0:
        latest_filename = result.stdout.decode('utf-8').strip()
        with open(latest_filename,"r") as file:
            latest_diff_config = file.read()

        diff_lines = list(ndiff(latest_diff_config.splitlines(keepends=True), running_config['running'].splitlines(keepends=True)))

        diff += f"Displaying the difference between the current running configuration of {hostname} and the last saved running-configuration in {latest_filename}<br/>"
        for line in diff_lines:
            if line.startswith('-') or line.startswith('+'):
                diff += f"{line}<br/>"
        diff += "<br/>--------------------------------------------------<br/>"
    
    else:
        diff += f"No latest config file found for {hostname}"
    
    return diff


def diffConfig():
    credentials = sshInfo()
    diff = ""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for hostname, info in credentials.items():
            device_type = info["Device_Type"]
            device_ip = info["IP"]
            device_username = info["Username"]
            device_password = info["Password"]

            future = executor.submit(diff_config, hostname, device_type, device_ip, device_username, device_password)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            diff += future.result()

    return diff


if __name__ == "__main__":
    print(diffConfig())