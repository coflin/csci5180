#!/usr/bin/python3
import bgp
import concurrent.futures
from connectivity import checkConnectivity
from sshInfo import sshInfo
from validateIP import validateIP

def main():
    credential = sshInfo()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(checkConnectivity, (credential[f'R{i}'] for i in range(1,3)))
        executor.map(validateIP, (credential[f'R{i}'] for i in range(1, 3)))
    
    bgp.main(credential)

if __name__ == "__main__":
    main()