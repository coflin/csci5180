#!/usr/bin/python3

from netmiko import ConnectHandler
from sshInfo import sshInfo

def ping_r5(net_connect,r5_ipv6):
    net_connect.send_command(f"ping ipv6 {r5_ipv6} repeat 2")

def connect_r5(r5_ipv6):
    ios = {
        "device_type":sshInfo()["R5"]["Device_Type"],
        "ip":r5_ipv6,
        "username":sshInfo()["R5"]["Username"],
        "password":sshInfo()["R5"]["Password"]
    }

    try:
        nc = ConnectHandler(**ios)
        return nc
    
    except Exception as e:
        print(f"Unable to connect to R5: {e}")


def configure_dhcpv4(r2r3_macaddr_dict):
    
    r4_ip = sshInfo()["R4"]["IP"]
    r4_username = sshInfo()["R4"]["Username"]
    r4_password = sshInfo()["R4"]["Password"]
    r4_devicetype = sshInfo()["R4"]["Device_Type"]

    ios = {
        "device_type":r4_devicetype,
        "ip":r4_ip,
        "username":r4_username,
        "password":r4_password
        }

    try:
        net_connect = ConnectHandler(**ios)

        r5_linklocal = sshInfo()["R5"]["IPv6"]
        ping_r5(net_connect,r5_linklocal)

        output = net_connect.send_command("show ipv6 neighbors")
        for line in output.splitlines()[1:]:
            if "REACH" in line and "Fa0/0" in line:
                mac_addr = line.split()[2]
                if mac_addr != r2r3_macaddr_dict["R2"] and mac_addr != r2r3_macaddr_dict["R3"]:
                    r5_ip = line.split()[0]

        nc_r5 = connect_r5(r5_ip)
        
        #Configuring DHCPv4
        
        r2_mac = r2r3_macaddr_dict["R2"]
        r2_mac = r2_mac.replace(":","")
        r2_mac = "01"+r2_mac
        r2_client_id = '.'.join([r2_mac[i:i+4] for i in range(0, len(r2_mac), 4)])

        r3_mac = r2r3_macaddr_dict["R3"]
        r3_mac = r3_mac.replace(":","")
        r3_mac = "01"+r3_mac
        r3_client_id = '.'.join([r3_mac[i:i+4] for i in range(0, len(r3_mac), 4)])


        print("Configuring DHCPv4 server on R5..")
        commands = [
            "ip dhcp excluded-address 198.51.200.0 198.51.200.3",
            "ip dhcp excluded-address 198.51.200.5",
            "ip dhcp pool R2",
            "host 198.51.200.2 255.255.255.0",
            f"client-identifier {r2_client_id}",
            "exit",
            "ip dhcp pool R3",
            "host 198.51.200.3 255.255.255.0",
            f"client-identifier {r3_client_id}",
            "exit",
            "ip dhcp pool others",
            "network 198.51.200.0 255.255.255.0"
            ]
        
        nc_r5.send_config_set(commands)
        device_output=nc_r5.send_command("show ip dhcp binding")
        print("Configured DHCPv4 Server on R5\n\n")
        print(device_output)


    except Exception as e:
        print(f"Error connecting to device: {e}")

    
        

if __name__ == "__main__":
    configure_dhcpv4()
