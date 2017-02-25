# Cisco Meraki Firewall AP Rules API
Python script that list/update your Cisco Meraki AP (Wireless) Firewall rules

![](https://raw.githubusercontent.com/robertcsapo/cisco-meraki-fw-ap-rules-api/master/demo.gif)

# Features

- List your current firewall rules on a SSID
- Override your current firewall rules through user input (csv format)
- Import csv file (sample.fw.csv)
- List all your SSIDs (associated with your API key)
- Docker support
  - https://hub.docker.com/r/robertcsapo/cisco-meraki-fw-ap-rules-api/
- Support for Docker Secrets Management (MERAKI_TOKEN as ENV)
  - https://blog.docker.com/2017/02/docker-secrets-management/
- Debug

# Help
```
Cisco Meraki AP Firewall Rules API - Help section

optional arguments:
  -h, --help         show this help message and exit
  --token TOKEN      Meraki token (if not using ENV)
  --list-networks    List all the Network id and Org id associated with your
                     API token
  --network NETWORK  Network id (Wireless/Templates)
  --ssid SSID        SSID id (0-14)
  --csv CSV          Import rules from CSV file
  --yes              Assume Yes to all queries and do not prompt
  --debug            Debug JSON Payload or when listing networks
```

# Docker support
# Run
### Interactive
```
docker run --rm -it robertcsapo/cisco-meraki-fw-ap-rules-api:latest --token <token> --network <network_id> --ssid <0-14>
```
### CSV import
```
docker run --rm -it -v $PWD:/data/export/ robertcsapo/cisco-meraki-fw-ap-rules-api:latest --token <token> --network <network_id> --ssid <0-14> --csv /data/export/sample.fw.csv
```
### CSV import with non-interactive
```
docker run --rm -it -v $PWD:/data/export/ robertcsapo/cisco-meraki-fw-ap-rules-api:latest --token <token> --network <network_id> --ssid <0-14> --yes --csv /data/export/sample.fw.csv
```
## Build
```
docker build -t robertcsapo/cisco-meraki-fw-ap-rules-api:latest .
```
# License
MIT
