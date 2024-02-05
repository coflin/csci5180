#!/usr/bin/python

import os
os.sys.path.append('/usr/bin/')
from scapy.all import *

dst_ip = "10.0.0.3"

pingr1 = sr1(IP(dst="10.0.0.3")/ICMP())
print(pingr1.show())