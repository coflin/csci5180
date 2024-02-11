#!/usr/bin/python3

try:
    import csv
    from loguru import logger

except ModuleNotFoundError:
    print("Please run 'pip3 install loguru' before running this code")

def sshInfo():
    try:
        with open("sshInfo.csv","r") as file:
            credentials = csv.DictReader(file)            
            cred = [credential for credential in credentials]
            return cred[0]
        
    except FileNotFoundError:
        logger.error("sshInfo.csv not found. Please check and try again.")

if __name__ == "__main__":
    sshInfo()