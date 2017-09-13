# reconnect_E5186
Python script for Raspberry pi board (or any linux pc) which force reconnecting with network in case of failed ping

## Installation
  1. Put script in your home directory
  2. Add job to cron:
  
    */1 * * * * /usr/bin/python ~/reconnect_E5186/reconnect_E5186.py 2>&1
    
  Script will be executed every 1 minute (*/1 part of cron command)
