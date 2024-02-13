#!/usr/bin/python3

try:    
    import concurrent.futures
    from loguru import logger
    from sshInfo import sshInfo
    import subprocess

except ModuleNotFoundError:
    print("Please run 'pip3 install loguru futures' before running this code")


def checkConnectivity(ipaddr):
    try:
        subprocess.check_call(['ping','-c2',ipaddr],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        logger.info(f"{ipaddr} is reachable")

    except subprocess.CalledProcessError:
        logger.error(f"{ipaddr} is not reachable")

def main():
    credentials = sshInfo()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(checkConnectivity, (credentials[f'R{i}'] for i in range(1,3)))

if __name__ == "__main__":
    main()