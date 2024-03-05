#!/usr/bin/python3

from scapy.all import *


def bin_to_hex(binary):    
    decimal_number = int(binary, 2)
    hexadecimal_number = hex(decimal_number)
    return hexadecimal_number[2:]


def hex_to_bin(hex):
    binary = ''.join(format(int(hex, 16), '04b'))
    return binary

def find_macaddr():
    print("Analyzing ping6.pcap file..")
    pcap_file = "ping6.pcap"
    packets = rdpcap(pcap_file)

    routers_ipv6 = {}
    routers_mac = {}

    for packet in packets:
        if packet.haslayer(Ether) and packet.haslayer(IPv6) and packet.haslayer(ICMPv6EchoRequest):
            ipv6 = packet[IPv6]
            icmpv6_echo = packet[ICMPv6EchoRequest]
            routers_ipv6[icmpv6_echo.id]=ipv6.src

    routers = list(routers_ipv6.values())

    print("Retreiving R2 nad R3 MAC address..")
    for i in range(len(routers)):
        router = routers[i]
        router_mac = router.split("2001:db8:0:1:")[1].split("ff:fe")
        router_mac = router_mac[0]+router_mac[1]

        #to flip the 7th bit from left:
        binary = hex_to_bin(router_mac[1])
        flipped_binary = binary[:-2]+str(int(binary[-2])^1)+binary[-2+1:]

        hexa = bin_to_hex(flipped_binary)

        final_mac = router_mac[:1]+hexa+router_mac[1+1:]

        sections = final_mac.split(":")

        for j, section in enumerate(sections):
            if len(section) < 4:
                sections[j] = section.zfill(4)

        final_mac = ":".join(sections)
        routers_mac[f"R{i+2}"] = final_mac

    print(routers_mac)
    return routers_mac

if __name__ == "__main__":
    find_macaddr()