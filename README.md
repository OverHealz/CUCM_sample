# CUCM_sample
The program forms a sample from Cisco Call Manager using AXL. The result is saved in XLSX format.</br>
Works on Linux, Windows.

## Use
To obtain a report run:</br>
>./get_report.py

![](/screenshot/scrsht.png)

The program reads the config file cucm_param.conf  and establish the connection with CUCM for report generating.
If the config file is empty or does not exist, it must be created before run.
To create the config file run:</br>
>./set_config.py

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
   and unpckt it to /resources folder of the project.
5. Install the SOAP client:</br>
>pip install zeep

### License

This project is licensed under the MIT License.

