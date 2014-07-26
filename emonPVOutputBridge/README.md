# emonPVOutputBridge

This is a Python3 application for connecting you EmonCMS installation to PVOutput.

### Installation
Installation is simple, do a `git clone https://github.com/peeter123/emonTxV3.git` and copy config.ini.dist to
config.ini in the emonPVOutputBridge folder. The rest of the instructions are for Ubuntu/Debian like distributions.
I run the application on the RaspberryPi next to Emonhub.

#### Dependencies
Install dependencies by running `sudo pip3 install -r Requirements.txt` in the emonPVOutputBridge directory.

### Configuration
The application can be configured by editing config.ini. Set the correct apikeys and feedids for both EmonCMS and
PVOutput.

### Running
For now there is no upstart script available. The application can be ran by running:  
```
screen python3 main.py
```  
To start the application on boot, add the following to `sudo crontab -e`:  
```
@reboot screen -dmS epvb /usr/bin/python3 /dir/to/emonTxV3/emonPVOutputBridge/main.py
```