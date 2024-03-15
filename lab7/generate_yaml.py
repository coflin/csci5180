#!/usr/bin/python3

import yaml

def main():
    # Data for routers
    routers_data = [
        {
            "hostname": "R1",
            "loopback": {"ip": "10.0.0.1", "subnet_mask": "255.255.255.255", "ospf_enabled": True, "wildcard": "0.0.0.0"},
            "fa0/0": {"ip": "198.51.100.1", "subnet_mask": "255.255.255.0", "ospf_enabled": True, "wildcard": "0.0.0.255"},
            "fa1/0": {"ip": "198.51.101.1", "subnet_mask": "255.255.255.0", "ospf_enabled": True, "wildcard": "0.0.0.255"},
            "ospf_process_id": 1,
            "ospf_area": 0
        },
        {
            "hostname": "R2",
            "loopback": {"ip": "20.0.0.1", "subnet_mask": "255.255.255.255", "ospf_enabled": True, "wildcard": "0.0.0.0"},
            "fa0/0": {"ip": "198.51.100.3", "subnet_mask": "255.255.255.0", "ospf_enabled": True, "wildcard": "0.0.0.255"},
            "fa1/0": {"ip": "198.51.101.2", "subnet_mask": "255.255.255.0", "ospf_enabled": True, "wildcard": "0.0.0.255"},
            "fa2/0": {"ip": "198.51.102.1", "subnet_mask": "255.255.255.0", "ospf_enabled": True, "wildcard": "0.0.0.255"},
            "ospf_process_id": 2,
            "ospf_area": 0       
        },
        {
            "hostname": "R3",
            "loopback": {"ip": "30.0.0.1", "subnet_mask": "255.255.255.255", "ospf_enabled": True, "wildcard": "0.0.0.0"},
            "fa0/0": {"ip": "198.51.100.4", "subnet_mask": "255.255.255.0", "ospf_enabled": True, "wildcard": "0.0.0.255"},
            "fa1/0": {"ip": "198.51.102.2", "subnet_mask": "255.255.255.0", "ospf_enabled": True, "wildcard": "0.0.0.255"},
            "ospf_process_id": 3,
            "ospf_area": 0
        }
    ]

    # Data for tasks/main.yaml
    tasks_main_yaml = [
        {
            "name": "Generate configuration files",
            "template": {
                "src": "router_config.j2",
                "dest": "/home/student/git/csci5180/lab7/cfgs/{{ item.hostname }}.txt"
            },
            "with_items": "{{ routers }}"
        }
    ]

    # Data for router_config.yaml
    site_yaml = [
        {
            "name": "Generate configuration files",
            "hosts": "localhost",
            "roles": ["router"]
        }
    ]

    # Write routers data to YAML file
    with open("roles/router/vars/main.yaml", "w") as routers_file:
        yaml.dump({"routers": routers_data}, routers_file, sort_keys=False)

    # Write tasks/main.yaml data to YAML file
    with open("roles/router/tasks/main.yaml", "w") as tasks_main_file:
        yaml.dump(tasks_main_yaml, tasks_main_file, sort_keys=False)

    # Write router_config.yaml data to YAML file
    with open("router_config.yaml", "w") as site_file:
        yaml.dump(site_yaml, site_file, sort_keys=False)

if __name__ == "__main__":
    main()