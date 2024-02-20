#!/usr/bin/python3

try:
    import concurrent.futures
    import ipaddress
    #from loguru import logger
    from sshInfo import sshInfo

except ModuleNotFoundError:
    print("Please 'pip3 install loguru futures' before running this code")

def isValid(ipaddr):
    try:
        ipaddress.ip_address(ipaddr)
        return True
        #logger.info(f"{ipaddr} is valid")

    except ValueError:
        #logger.error(f"{ipaddr} not valid. Please check and try again.")
        return False

def main():
    credentials = sshInfo()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(validateIP, (credentials[f'R{i}'] for i in range(1, 3)))

if __name__ == "__main__":
    main()
