###
### Cisco Meraki Firewall AP Rules API - robert@nigma.org
###
#!/usr/bin/env python

# Table layout
from tabulate import tabulate
# Progress bar
from tqdm import tqdm
import json
import requests
import sys
import os
import csv
import argparse

# Main Function
def main():
    if meraki_debug == "1":
        print("Debug enabled")
        print("Args: %s" % args)

    # If using arg --list-network, then print a table with all the network ssid associated with this Meraki API Token
    if args.list_networks is True:
        list_networks = meraki_list_networks()

    global fw_ap_list
    global fw_ap_list_raw
    global fw_ap_list_upload
    print("")
    print("- List Firewall rules (AP) -")
    fw_ap_list = meraki_ap_fw_rules("pre")

    # Import Firewall rules from CSV file, if using arg --csv
    if args.csv:
        print("- Importing CSV file %s -" % args.csv)
        print("")
        fw_ap_list_upload = meraki_ap_fw_rules_import_csv(args.csv)
        print("")

    # User input for override the firewall rules
    else:
        print("- Add your new firewall rule below (end by double hitting ENTER or exit through Ctrl-C) =>")
        lines = []
        try:
            while True:
                line = input()
                if line.lower() == "exit":
                    sys.exit("- User typed 'exit', exiting... -")
                if line:
                    lines.append(line)
                else:
                    break
        except KeyboardInterrupt:
            print("")
            sys.exit("- User pressed CTRL-C, exiting... -")
        if len(lines) == 0:
            sys.exit("- No input for Firewall rules, exiting... -")
        for item in lines:

            # Split by , (csv support)
            fw_ap_list_upload.append(item.split(","))

    # Assume Yes based on arg
    if args.yes:
        print("- Do you want to update the firewall rules with your input? (exit by pressing CTRL-C) => yes")
        print("- We'll send the data now... -")
        print(tabulate(fw_ap_list_upload,headers=['Policy','Protocol','Destination','Port','Comment'],tablefmt="rst"))
        # Creating the JSON Payload
        fw_ap_list_upload_json = {}
        fw_ap_list_upload_json["rules"] = []
        for item in fw_ap_list_upload:
            if item[2] != "Local LAN" and item[2] != "Any":
                fw_ap_list_upload_json["rules"].append({"comment": item[4],"policy": item[0],"protocol": item[1],"destPort": item[3],"destCidr": item[2]})
        if meraki_debug == "1":
            print("JSON Payload")
            print(fw_ap_list_upload_json)
            print("")
        url = "/networks/%s/ssids/%s/l3FirewallRules" % (args.network,args.ssid)
        send_data = meraki_put(url,meraki_api_key,fw_ap_list_upload_json)
    else:
        # Verify CSV import or user input
        try:
            while True:
                confirm_input = input("- Do you want to update the firewall rules with your input? (exit by pressing CTRL-C) => ")
                confirm_input = confirm_input.lstrip() # Ignore leading space
                if confirm_input == 'yes' or confirm_input == "y":
                    print("- We'll send the data now... -")
                    print(tabulate(fw_ap_list_upload,headers=['Policy','Protocol','Destination','Port','Comment'],tablefmt="rst"))
                    # Creating the JSON Payload
                    fw_ap_list_upload_json = {}
                    fw_ap_list_upload_json["rules"] = []
                    for item in fw_ap_list_upload:
                        if item[2] != "Local LAN" and item[2] != "Any":
                            fw_ap_list_upload_json["rules"].append({"comment": item[4],"policy": item[0],"protocol": item[1],"destPort": item[3],"destCidr": item[2]})
                    if meraki_debug == "1":
                        print("JSON Payload")
                        print(fw_ap_list_upload_json)
                        print("")
                    url = "/networks/%s/ssids/%s/l3FirewallRules" % (args.network,args.ssid)
                    send_data = meraki_put(url,meraki_api_key,fw_ap_list_upload_json)
                    break
                else:
                    sys.exit("- User typed something else then 'yes' or 'y' - exiting... -")
        except KeyboardInterrupt:
            print("")
            sys.exit("- User pressed CTRL-C, exiting... -")
    sys.exit(" - Done, exiting... -")

# Meraki REST API Call - GET
def meraki_requests(url,meraki_api_key,error_handle):
    url = "https://dashboard.meraki.com/api/v0%s" % url
    if meraki_debug == "1":
        print("GET: %s" % url)
    querystring = {}
    headers = {
        'x-cisco-meraki-api-key': meraki_api_key,
        'content-type': "application/json",
        'cache-control': "no-cache",
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        json_data = json.loads(response.text)
        return json_data
    else:
        if meraki_debug == "1":
            print(response.text)
        if error_handle == "enable":
            sys.exit("Failed: Code %s" % response.status_code)

# Meraki REST API Call - PUT
def meraki_put(url,meraki_api_key,payload):
    url = "https://dashboard.meraki.com/api/v0%s" % url
    if meraki_debug == "1":
        print("POST: %s" % url)
    global fw_ap_list
    global fw_ap_list_raw
    global fw_ap_list_upload
    global fw_ap_list_upload_json
    payload = json.dumps(payload)
    headers = {
    'x-cisco-meraki-api-key': meraki_api_key,
    'content-type': "application/json",
    'cache-control': "no-cache",
    }
    response = requests.request("PUT", url, data=payload, headers=headers)
    if response.status_code == 200:
        json_data = json.loads(response.text)
        # Reset global vars as firewalls are now updated
        fw_ap_list=[]
        fw_ap_list_raw=[]
        fw_ap_list_upload=[]
        fw_ap_list_upload_json=[]
        print("")
        print("- Successful... Display new FW rules table -")
        print("")
        if meraki_debug == "1":
            print(response.text)
            print("")
        # Prints the FW table again
        meraki_ap_fw_rules("post")
        return json_data
    else:
        print("Failed")
        if meraki_debug == "1":
            print(response.text)
        sys.exit("Failed: Code %s" % response.status_code)

# List all Firewall Rules
def meraki_ap_fw_rules(status):
    json_fw_ap_list = meraki_requests("/networks/%s/ssids/%s/l3FirewallRules" % (args.network,args.ssid),meraki_api_key, "enable")
    global fw_ap_list
    key=0
    for item in json_fw_ap_list:
        key +=1
        # If there's only 2 firewall rules, then that's propably only the default meraki rules (which has their own string vars)
        if len(json_fw_ap_list) == 2:
            fw_ap_list.append([item["policy"],item["proto"],item["dst_cidr"],item["dst_port"],item["comment"]])
        else:
            # Split by , (csv support)
            fw_ap_list_raw.append([item["policy"]+','+item["protocol"]+','+item["destCidr"]+','+item["destPort"]+','+item["comment"]])
            fw_ap_list.append([item["policy"],item["protocol"],item["destCidr"],item["destPort"],item["comment"]])
    print(tabulate(fw_ap_list,headers=['Policy','Protocol','Destination','Port','Comment'],tablefmt="rst"))
    if status == "pre":
        print("")
        print(tabulate(fw_ap_list_raw,headers=['- Copy paste output (use as template) -'],tablefmt="rst"))
    print("")
    return fw_ap_list

# Import CSV file
def meraki_ap_fw_rules_import_csv(filename):
    fw_ap_import_csv_list = []
    try:
        with open(filename) as csvfile:
            fw_ap_import_csv = csv.reader(csvfile, delimiter=',')
            key=0
            for item in fw_ap_import_csv:
                if key != 0:
                    print(item)
                    fw_ap_import_csv_list.append(item)
                    if len(item) < 5:
                        key +=1
                        print("")
                        sys.exit("- Error: Row %s isn't correct, exiting... -" % key)
                key +=1
        return fw_ap_import_csv_list
    except FileNotFoundError:
        sys.exit("- Error: CSV file not found %s, exiting... -" % filename)

def meraki_list_networks():
    org_list = meraki_org()
    print("- Gathering all the networks from %s organizations -" % len(org_list))
    with tqdm(desc='Progess',total=(len(org_list))) as pbar:
        # Loop through every Org
        for item in org_list:
            url = "/organizations/%s/networks" % item[0]
            # Get all the networks based on Org
            json_data_network = meraki_org_networks(item[0])
            if json_data_network:
                if meraki_debug == "1":
                    print("API Enabled")
            else:
                if meraki_debug == "1":
                    print("Network ID %s" % item[0])
                    print("API Access Disabled")
            pbar.update(1)
    if meraki_debug == "1":
        print(tabulate(networks_list,headers=['Network ID','Network Name',"Org ID"],tablefmt="rst"))
    print("- Creating a table with all the SSID from %s networks in %s organizations -" % (len(networks_list), len(org_list)))
    with tqdm(desc='Progess',total=(len(networks_list))) as pbar:
        # Loop through every network
        for item in networks_list:
            pbar.update(1)
            # Get SSID data from Network ID
            json_data_networks_ssid = meraki_org_networks_ssid(item[0],item[1],item[2])
    print("")
    print(tabulate(networks_list_ssid,headers=['Network ID','Network Name',"Organization ID","SSID","Number","Status"],tablefmt="rst"))
    print("")
    sys.exit("- Done, exiting... -")

# List all org id
def meraki_org():
    json_data_org = meraki_requests("/organizations/",meraki_api_key, "enable")
    org_list=[]
    for item in json_data_org:
        org_list.append([item["id"],item["name"]])
    if meraki_debug == "1":
        print(tabulate(org_list,headers=['Org ID','Name'],tablefmt="rst"))
    return org_list

# List all the network id with org id
def meraki_org_networks(network_id):
    url = "/organizations/%s/networks" % network_id
    json_data_networks = meraki_requests(url,meraki_api_key,"disable")
    global networks_list
    if json_data_networks:
        for item in json_data_networks:
            networks_list.append([item["id"],item["name"],item["organizationId"]])
        if meraki_debug == "1":
            print(tabulate(networks_list,headers=['Network ID','Network Name',"Org ID"],tablefmt="rst"))
        return networks_list

# List all SSID on network id with org id
def meraki_org_networks_ssid(network_id,network_name,org_id):
    url = "/networks/%s/ssids" % network_id
    json_data_networks_ssid = meraki_requests(url,meraki_api_key,"disable")
    global networks_list_ssid
    if json_data_networks_ssid:
        for item in json_data_networks_ssid:
            if item["enabled"] is True:
                item["enabled"] = "Enabled"
            if item["enabled"] is False:
                item["enabled"] = "Disabled"
            networks_list_ssid.append([network_id,network_name,org_id,item["name"],item["number"],item["enabled"]])
        if meraki_debug == "1":
            print(tabulate(networks_list_ssid,headers=['Network ID','Network Name',"Organization ID","SSID","Number","Status"],tablefmt="rst"))
        return networks_list

# Start script if running as standalone
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Cisco Meraki Firewall AP Rules API - Help section')
    parser.add_argument('--token',
                            help='Meraki token (if not using ENV)')
    parser.add_argument('--list-networks', action='store_true',
                            help='List all the Network id and Org id associated with your API token')
    parser.add_argument('--network',
                            help='Network id (Wireless/Templates)')
    parser.add_argument('--ssid',
                            help='SSID id (0-14)')
    parser.add_argument('--csv',
                            help='Import rules from CSV file')
    parser.add_argument('--yes', action='store_true',
                            help='Assume Yes to all queries and do not prompt')
    parser.add_argument('--debug', action='store_true',
                            help='Debug JSON Payload or when listing networks')

    # If args are missing, print help
    if len(sys.argv[1:])==0:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    # No point to assume yes on all queries if user hasn't imported firewall rules
    if args.yes and args.csv is None:
        parser.error("--yes requires --csv")

    if args.token:
        os.environ['MERAKI_TOKEN'] = args.token
    if 'MERAKI_TOKEN' in os.environ:
        meraki_api_key = os.environ['MERAKI_TOKEN']
    else:
        try:
            meraki_api_key
        except:
            parser.error("--token required if MERAKI_TOKEN isn't set")

    if 'MERAKI_DEBUG' in os.environ:
        meraki_api_key = os.environ['DEBUG']
    else:
        meraki_debug = "0"
    if args.debug:
        meraki_debug = "1"

    # Create global variables
    networks_list=[]
    networks_list_ssid=[]
    fw_ap_list=[]
    fw_ap_list_raw=[]
    fw_ap_list_upload=[]

    main()
