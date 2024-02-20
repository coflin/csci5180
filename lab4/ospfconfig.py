from napalm import get_network_driver
from cidr_wildcard import cidr_wildcard
from prettytable import PrettyTable
from validateIP import isValid
from sshInfo import sshInfo
import concurrent.futures

def connectRouter(device_type, router_ip, username, password):
    driver = get_network_driver(device_type)
    device = driver(hostname=router_ip, username=username, password=password)
    device.open()

    command = "show interfaces Loopback0 | include Internet address is"

    output = device.cli([command])

    loopback0_ip = output[command].split("/")[0].split()[3]

    return loopback0_ip, device

def configureOSPF(device, ospf_process, ospf_advertise):
    cidr_wildcard_dict = cidr_wildcard()
    commands = f"router ospf {ospf_process}\n"

    for network in ospf_advertise:
        cidr, area = network.split(":")
        ip, netmask = cidr.split("/")
        wildcardmask = cidr_wildcard_dict[f"/{netmask}"]

        int_command = f"show ip route {ip}"
        output = device.cli([int_command])

        if "%" in output[int_command] or not isValid(ip):
            return False, "OSPF advertised IP address is not valid or not configured on network."
        else:
            commands += f"network {ip} {wildcardmask} area {area}\n"

    commands += "!\n"

    return True, commands

def configureOSPFAndRedirect(router_index, routers, router, loopbackip, loopback0_ip, device, ospfprocess, ospfadvertise):
    if isValid(loopbackip) and loopbackip == loopback0_ip:
        success, commands = configureOSPF(device, ospfprocess, ospfadvertise)
        if success:
            device.open()
            device.load_merge_candidate(config=commands)

            table = PrettyTable(["Interface", "IP Address"])
            interfaces = device.get_interfaces_ip()
            for interface, ip in interfaces.items():
                table.add_row([interface, list(ip['ipv4'].keys())[0]])
            print(table)

            # Commit the configuration changes in a separate thread with a timeout
            with concurrent.futures.ThreadPoolExecutor() as executor:
                commit_future = executor.submit(device.commit_config)
                try:
                    # Wait for the commit_config() operation to complete with a timeout of 60 seconds
                    commit_future.result(timeout=60)
                except concurrent.futures.TimeoutError:
                    # Handle timeout error
                    pass  # Ignore timeout error and proceed

            if router_index + 1 < len(routers):
                # Proceed to the next router
                return True, None, router_index + 1
            else:
                # All routers configured, proceed with ping
                ping_result = ping_loopback_addresses()
                return True, f"All routers configured with OSPF successfully. Ping result: \n{ping_result}", None

            device.close()

        else:
            error_message = commands  # Error message from configureOSPF
            return False, error_message, None
    else:
        error_message = "Loopback IP address is not valid or does not match config on the router"
        return False, error_message, None

def ping_loopback_addresses():
    # Connect to R1
    driver = get_network_driver('ios')
    device = driver(hostname=sshInfo()["R1"]["IP"], username=sshInfo()["R1"]["Username"], password=sshInfo()["R1"]["Password"])
    device.open()

    # Retrieve loopback addresses from R1
    loopback_addresses = ['10.0.0.1', '20.0.0.1', '30.0.0.1', '40.0.0.1'] 

    # Execute ping commands for each loopback address
    ping_results = ""
    for address in loopback_addresses:
        output = device.ping(address)
        result = list(output.keys())[0]
        ping_results += f"{address}: {result}\n"

    # Close the connection
    device.close()

    return ping_results