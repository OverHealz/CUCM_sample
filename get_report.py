#!/usr/bin/python3
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep import xsd
from pathlib import Path
import pandas as pd
import numpy as np
import urllib3
import base64
import sys
import os
os.system("")

def main():
    global conf
    conf = dict({"cucm_ip": "", "cucm_user": "", "cucm_pwd": "", "wsdl_uri": ""})
    try:
        cfg_file = open(r"cucm_param.conf", "r", encoding="utf-8")
    except FileNotFoundError:
        print("\033[91m" + "Config file not found" +  "\033[0m")
        sys.exit(1) 
    if read_cucm_param(cfg_file) == 0:
        get_info_from_cucm(conf)
    cfg_file.close()

# ----------------------------------------------------------------------------------
def read_cucm_param(cfg_file):
    for line in cfg_file:
        i = 0
        par = ""
        znach = ""
        if (line.lstrip()).rstrip() != "":
            while line[i] != ':':
                par = "".join((par,line[i]))
                i = i + 1 
            znach = ((line[i+1:-1]).lstrip()).rstrip()
            if par == "CUCM_IP":
                if znach == "":
                    print("Set IP address of CUCM in cucm_param.conf")
                    return -1
                else:
                    conf["cucm_ip"] = znach
            elif par == "CUCM_USER":
                if znach == "":
                    print("Set user name in cucm_param.conf")
                    return -1
                else:
                    conf["cucm_user"] = znach
            elif par == "CUCM_PASSWORD":
                if znach == "":
                    print("Set user encrypted password in cucm_param.conf")
                    return -1
                else:
                    conf["cucm_pwd"] = znach
    return 0

def get_info_from_cucm(conf):
    CUCM_USERNAME = conf["cucm_user"]
    CUCM_PASSWD = base64.b64decode(conf["cucm_pwd"]).decode("utf-8")
    CUCM_URL = "".join(("https://",conf["cucm_ip"],":8443/axl/"))
    WSDL_URL = "file://" + Path("resources/AXLAPI.wsdl").absolute().as_posix()

    print("cucm_url =", CUCM_URL)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = Session()
    session.verify = False
    session.auth = HTTPBasicAuth(CUCM_USERNAME, CUCM_PASSWD)
    transport = Transport(session=session, timeout=10, cache=SqliteCache())

    try:
        client = Client(WSDL_URL, transport=transport)
    except:
        print("\033[91m" + "Can't load WSDL file" +  "\033[0m")
        sys.exit(1) 

    try:
        service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)
    except Exception as some_error:
        print(f'Connection error: {some_error}')
        sys.exit(1) 

    try:
        ver = service.getCCMVersion()
    except Exception as some_error:
        print("\033[91m" + "Can't connect to CUCM" + "\033[0m")
        sys.exit(1) 

    print("\033[92m" + "Connected!" +  "\033[0m")
    print("CUCM version:", "\033[92m" , ver['return']['componentVersion']['version'], "\033[0m")

    retTags = {
                'name': "",
                'description': "",
                'product': "",
                'model': "",
                'protocol': "",
                'protocolSide': "",
                'callingSearchSpaceName': "",
                'devicePoolName': "",
                'commonDeviceConfigName': "",
                'commonPhoneConfigName': "",
                'networkLocation': "",
                'locationName': "",
                'sipProfileName': "",
                'numberOfButtons': "",
                'primaryPhoneName': "",
                'userLocale': "",
                'networkLocale': "",
                'loginTime': "",
                'loginDuration': "",
                'ownerUserName': "",
                'unattendedPort': "",
                'requireDtmfReception': "",
                'certificateOperation': "",
                'authenticationMode': "",
                'certificateStatus': "",
                'isActive': "",
                'isDualMode': "",
                'phoneSuite': "",
                'phoneServiceDisplay': "",
                'isProtected': "",
            }
    Criteria = {"name": "%"}

    try:
        rezult = service.listPhone(searchCriteria = Criteria, returnedTags = retTags)
    except Exception as some_error:
        print(f'Error during exec listPhone(): {some_error}')
        sys.exit(1) 

    total_ip_phones = len(rezult['return']['phone'])
    print("Total IP phones count:", "\033[92m", total_ip_phones, "\033[0m")

    df = pd.DataFrame(
            { "name": [],
              "description": [],
              "product": [],
              "model": [],
              "protocol": [],
              "devicePoolName": [],
              "locationName": [],
              "loginUserId": [],   
              "loginTime": [],   
              "loginDuration": [],   
              "callingSearchSpaceName": [],
              "ownerUserName": [],
              "isActive": []
             }
           )
    cols = df.shape[1]
    row = 0
    for unit in range(0, total_ip_phones):
        df.loc[row] = np.nan
        df.iat[row,0] = rezult['return']['phone'][unit]["name"]
        df.iat[row,1] = rezult['return']['phone'][unit]["description"]
        df.iat[row,2] = rezult['return']['phone'][unit]["product"]
        df.iat[row,3] = rezult['return']['phone'][unit]["model"]
        df.iat[row,4] = rezult['return']['phone'][unit]["protocol"]
        df.iat[row,5] = rezult['return']['phone'][unit]["devicePoolName"]['_value_1']
        df.iat[row,6] = rezult['return']['phone'][unit]["locationName"]['_value_1']
        df.iat[row,7] = rezult['return']['phone'][unit]["loginUserId"]
        df.iat[row,8] = rezult['return']['phone'][unit]["loginTime"]
        df.iat[row,9] = rezult['return']['phone'][unit]["loginDuration"]
        df.iat[row,10] = rezult['return']['phone'][unit]["callingSearchSpaceName"]['_value_1']
        df.iat[row,11] = rezult['return']['phone'][unit]["ownerUserName"]['_value_1']
        df.iat[row,12] = rezult['return']['phone'][unit]["isActive"]
        row = row + 1

    wrt = pd.ExcelWriter(Path("report/report.xlsx").absolute().as_posix(), engine="xlsxwriter")
    df.to_excel(wrt, startrow = 1, header = False, index = False)
    wb = wrt.book
    wsheet = wrt.sheets['Sheet1']
    header_format = wb.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'center',
        'fg_color': '073a67',
        'color': 'cyan',
        'border': 2})

    for col, value in enumerate(df.columns.values):
        wsheet.write(0, col, value, header_format)
    wrt.close()
    print("The report was generated in the file:", "\033[92m"+"report.xlsx"+"\033[0m")


if __name__ == '__main__':
    main()
