# CUCM_sample
The program forms a sample from Cisco Call Manager using AXL. The result is saved in XLSX format.</br>
Works on Linux, Windows.</br>
Tested on CUCM v.12.5, v.14

## Use
Two working options are presented for unloading information from CUCM:
1. By executing an SQL query against the Informix CUCM database.</br>
   To obtain a report run (for v.14):</br>
```
./get_report_by_sql.py
```
![](/screenshot/scrsht_v14.png)

   As a result, an XLSX table is formed:</br>
![](/screenshot/report_s.png)

2. Using the listPhone() function from the zeep.
   To obtain a report run (for v.12.5):</br>
```
./get_report.py
```
![](/screenshot/scrsht.png)

   An XLSX table is also formed here, the set of columns will be different.</br>

Before starting, you need to set the parameters.</br>
The program reads the config file cucm_param.conf  and establish the connection with CUCM for report generating.
If the config file is empty or does not exist, it must be created before run.
To create the config file run:</br>
```
./set_config.py
```

and set parameters:
- CUCM IP address
- Name of user, which has AXL-access to CUCM
- User's password

The password in the config file is in encrypted form.

>Warning!
>Storing a password, even in encrypted form, cannot guarantee complete security.
>Here, this option is used as a sample for test runs.

### Prerequisites

1. Enable the AXL SOAP Service on CUCM.
2. Create a group “AXLServiceUser”, which has the rights/permissions inside CUCM for allowing
   anyone that’s a member of this group access to the AXL information.
3. Create a user and add it to the above created access control group so that it can query AXL.
4. Download the CiscoAXL Toolkit (axlsqltoolkit.zip) from Cisco Unified CM Administration 
   application (the complete schema definition for different versions of Cisco Unified CM)
   and unpack it to /resources folder of the project.
5. Install the SOAP client:</br>
```
pip install zeep
```

### License

This project is licensed under the MIT License.

