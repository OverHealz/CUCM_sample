#!/usr/bin/python3
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep import xsd
from datetime import datetime as dt
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
    WSDL_URL = "file://" + Path("resources_v14/AXLAPI.wsdl").absolute().as_posix()

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

    sql = '''
            select d.name, d.description,  tdp.name as deviceprotocol, tm.name as model, tp.name as product, \
            rd.lastseen as last_registred, rd.lastactive as las_tactive, rd.lastknownucm as unified_cm \
            from device as d, registrationdynamic as rd,  typedeviceprotocol as tdp, typemodel as tm, typeproduct as tp \
            where d.pkid=rd.fkdevice and d.tkdeviceprotocol=tdp.enum and d.tkmodel=tm.enum and d.tkproduct=tp.enum
    '''
    try:
        resp = service.executeSQLQuery(sql)
    except Exception as some_error:
        print(f'SQL error: {some_error}')
        sys.exit(1) 

    df = pd.DataFrame(
            { "name": [],
              "description": [],
              "protocol": [],
              "model": [],
              "product": [],
              "last_registred": [],
              "last_active": [],
              "unified_cm": []
             }
           )

    cols = df.shape[1]
    row = 0
    for xml_row in resp[ 'return' ][ 'row' ]:
        df.loc[row] = np.nan
        df.iat[row,0] = xml_row[ 0 ].text
        df.iat[row,1] = xml_row[ 1 ].text
        df.iat[row,2] = xml_row[ 2 ].text
        df.iat[row,3] = xml_row[ 3 ].text
        df.iat[row,4] = xml_row[ 4 ].text
        stamp = int(xml_row[ 5 ].text)
        if stamp != 0:
            df.iat[row,5] = dt.fromtimestamp(stamp)
        stamp = int(xml_row[ 6 ].text)
        if stamp != 0:
            df.iat[row,6] = dt.fromtimestamp(stamp)
        df.iat[row,7] = xml_row[ 7 ].text
        row = row + 1

    wrt = pd.ExcelWriter(Path("report/report_s.xlsx").absolute().as_posix(), engine="xlsxwriter")
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
    print("The report was generated in the file:", "\033[92m"+"report_s.xlsx"+"\033[0m")


if __name__ == '__main__':
    main()
