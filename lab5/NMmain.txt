#!/usr/bin/python3

from NMtcpdump import find_macaddr
from NMdhcpserver import configure_dhcpv4
from NMsnmp import get_interface_details, check_cpu_utilization

def main():
    r2r3_macaddr_dict = find_macaddr()
    print("----------------------------")
    configure_dhcpv4(r2r3_macaddr_dict)
    print("----------------------------")
    get_interface_details()
    print("----------------------------")
    check_cpu_utilization('198.51.50.1')
    print("----------------------------")
if __name__ == "__main__":
    main()