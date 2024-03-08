#!/usr/bin/python3

from netmiko import ConnectHandler
import json

def main():
    ios = {
        "device_type":"cisco_ios",
        "ip":"198.51.100.1",
        "username":"snir8112",
        "password":"roomtoor"
    }

    nc = ConnectHandler(**ios)


    commands = ["ip dhcp excluded-address 198.51.200.1","ip dhcp pool r2pool","network 198.51.200.0 255.255.255.0","default-router 198.51.200.1","int Fa1/0", "ip address 198.51.200.1 255.255.255.0"]
    nc.send_config_set(commands)
    output = nc.send_command("show ip dhcp binding")

    r2ip = output.split()[20]

    ios_r2 = {
        "device_type":"cisco_ios",
        "ip":r2ip,
        "username":"snir8112",
        "password":"roomtoor"
    }

    nc2 = ConnectHandler(**ios_r2)
    output = nc2.send_command("ping 198.51.100.1")
    print(output)

if __name__ == "__main__":
    main()