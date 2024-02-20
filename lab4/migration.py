from napalm import get_network_driver
import time
import subprocess
from sshInfo import sshInfo
import threading

def ping_continuously(destination, completion_event):
    # Ping continuously to the specified destination
    while not completion_event.is_set():
        try:
            subprocess.run(["ping", "-c", "1", destination], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print("Waiting for connectivity...")
            time.sleep(1)
        else:
            print("Ping to destination successful.")
            completion_event.set()  # Set the event indicating successful ping

def get_tcp_traffic_stats(device_ip, username, password):
    driver = get_network_driver('ios')
    device = driver(hostname=device_ip, username=username, password=password)
    device.open()

    try:
        # Execute 'show ip traffic' command
        output = device.cli(["show ip traffic"])
        output = output['show ip traffic']

        # Extract TCP statistics
        tcp_rcvd = int(output.split("TCP statistics:")[1].splitlines()[1].split('Rcvd:')[1].split('total')[0].strip())
        tcp_sent = int(output.split("TCP statistics:")[1].splitlines()[2].split('Sent:')[1].split('total')[0].strip())

        return tcp_rcvd, tcp_sent

    except Exception as e:
        print(f"Error occurred: {e}")
        return None, None

    finally:
        device.close()

def migrate_r3(device_ip, username, password, interface):
    print(f"Starting migration process for device {device_ip}...")
    driver = get_network_driver('ios')
    device = driver(hostname=device_ip, username=username, password=password)
    device.open()

    try:
        # Configure banner motd
        banner_message = "Change made for migration in Lab 6"
        print(f"Configuring banner motd on device {device_ip} with message: '{banner_message}'")
        device.load_merge_candidate(config=f"banner motd ^{banner_message}^")
        device.commit_config()

        # Shutdown interface
        print(f"Shutting down interface {interface} on device {device_ip}")
        shutdown_config = f"interface {interface}\nshutdown\n"
        device.load_merge_candidate(config=shutdown_config)
        device.commit_config()
        time.sleep(2)
        print(f"Bringing the interface {interface} up")
        interface_up = f"interface {interface}\nno shutdown\n"
        device.load_merge_candidate(config=interface_up)
        device.commit_config()

        print(f"R3 migration completed successfully on device {device_ip}.")

    except Exception as e:
        print(f"Error occurred during migration: {e}")

    finally:
        device.close()

def mainMigration():
    credentials = sshInfo()

    r3_ip = sshInfo()["R3"]["IP"]
    r4_ip = sshInfo()["R4"]["IP"]
    username = sshInfo()["R3"]["Username"]
    password = sshInfo()["R3"]["Password"]
    interface_to_check = "FastEthernet1/0"  # Interface connected to SW2

    # Event to signal completion of ping
    completion_event = threading.Event()

    # Start continuous ping from R1 to R4 in a separate thread
    ping_thread = threading.Thread(target=ping_continuously, args=(r4_ip, completion_event))
    ping_thread.daemon = True  # Daemonize the thread so it terminates when the main thread terminates
    ping_thread.start()

    # Wait for ping to start
    time.sleep(1)

    # Get initial TCP statistics
    initial_tcp_rcvd, initial_tcp_sent = get_tcp_traffic_stats(r3_ip, username, password)

    # Wait for 5 seconds
    print("Monitoring TCP traffic for 5 seconds...")
    time.sleep(5)

    # Get final TCP statistics
    final_tcp_rcvd, final_tcp_sent = get_tcp_traffic_stats(r3_ip, username, password)

    # Calculate difference in TCP traffic
    tcp_rcvd_diff = final_tcp_rcvd - initial_tcp_rcvd
    tcp_sent_diff = final_tcp_sent - initial_tcp_sent

    if tcp_rcvd_diff < 100 and tcp_sent_diff < 100:
        # If traffic change is less than 100, proceed with migration
        print("No/Minimum traffic detected. Proceeding with the migration.")
        migrate_r3(r3_ip, username, password, interface_to_check)
    else:
        print("TCP traffic detected. Migration cannot proceed.")

    # Wait for ping completion
    completion_event.wait()
    print("Migration successful.")

if __name__ == "__main__":
    mainMigration()
