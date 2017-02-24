FROM python:3
MAINTAINER Robert (robert@nigma.org)

RUN DEBIAN_FRONTEND=noninteractive git clone https://github.com/robertcsapo/cisco-meraki-fw-ap-rules-api.git
WORKDIR /cisco-meraki-fw-ap-rules-api/
RUN DEBIAN_FRONTEND=noninteractive pip install -r requirements.txt

ENTRYPOINT [ "python", "./cisco_meraki_fw_ap_rules_api.py" ]
