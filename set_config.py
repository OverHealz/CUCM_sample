#!/usr/bin/python3
import base64
import os
import pwinput
os.system("")

def main():
    try:
        config = open(r"cucm_param.conf", "w", encoding="utf-8")
    except:
        print("\033[91m" + "Can't create config file" +  "\033[0m")
        sys.exit(1) 

    print("\033[;42m" + "Set parameters to connect to CUCM" + "\033[0m")
    ip_cucm = input("\033[92m" +"CUCM IP address: " + "\033[0m")
    axl_user = input("\033[92m" +"User name with AXL access: " + "\033[0m")
    axl_pwd = pwinput.pwinput(prompt="\033[92m" +"Password of user " +  axl_user + ": \033[0m", mask='*')
    encr_pwd = base64.b64encode(axl_pwd.encode('utf-8'))

    config.write("CUCM_IP: " + ip_cucm + "\n")
    config.write("CUCM_USER: " + axl_user + "\n")
    config.write("CUCM_PASSWORD: " + encr_pwd.decode("utf-8") + "\n")
    config.close()

    print("\033[;42m" + "File cucm_param.conf was generated" + "\033[0m")

if __name__ == '__main__':
    main()