#!/usr/bin/python3


def configure_ssh():
    ip domain name cub.com
    crypto key generate rsa modulus 2048
    ip ssh version 2
    username snir8112 password 0 roomtoor
    username snir8112 privilege 15
    aaa new-model
    line vty 0 15
    password 0 roomtoor
    transport input all 
    transport output all
    privilege level 15