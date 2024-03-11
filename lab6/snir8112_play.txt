#!/usr/bin/python3

packages = {'FTP server':'vsftpd','HTTP server':'apache2','pip':'python3-pip','expect':'expect'}


output = """
- name: Install essential packages
  hosts: footballservers
  become: true
  tasks:
"""

for key,value in packages.items():

    output += f"""
    - name: Install {key}
      apt:
        name: {value}
        state: present
        """

with open('snir8112_play.yaml','w') as file:
    file.write(output)

