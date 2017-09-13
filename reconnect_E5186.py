#!/usr/bin/env python

from __future__ import unicode_literals
#from PyCRC.CRC16 import CRC16

import requests
import re
import hashlib
import base64
import os, sys
import time


def dhcp(baseurl, session):
    data = '<request><DhcpIPAddress>192.168.1.1</DhcpIPAddress><DhcpLanNetmask>255.255.255.0</DhcpLanNetmask><DhcpStatus>1</DhcpStatus><DhcpStartIPAddress>192.168.1.100</DhcpStartIPAddress><DhcpEndIPAddress>192.168.1.200</DhcpEndIPAddress><DhcpLeaseTime>86400</DhcpLeaseTime><DnsStatus>1</DnsStatus><PrimaryDns>192.168.1.1</PrimaryDns><SecondaryDns>192.168.1.1</SecondaryDns></request>'
    r= session.post(baseurl + "api/dhcp/settings", data=data)
    print r.text

def login(baseurl, username, password):
    s = requests.Session()
    r = s.get(baseurl + "html/home.html")
    #print r.text
    csrf_tokens = grep_csrf(r.text)
    headers_update(s.headers, csrf_tokens[1])
    data = login_data(username, password, str(csrf_tokens[1]))
    r = s.request('POST', baseurl + "api/user/login", data=data)
    s.headers.update({'__RequestVerificationToken': r.headers["__requestverificationtokenone"]})
    print r.text
    return s

def logoff(baseurl, session):
  data = '<request><Logout>1</Logout></request>'
  r = session.request('POST', baseurl + "/api/user/logout", data=data)
  print r.text

def headers_update(dictbase, token):
    dictbase['Accept-Language'] = 'en-US'
    dictbase['Content-Type'] = 'application/x-www-form-urlencoded'
    dictbase['X-Requested-With'] = 'XMLHttpRequest'
    dictbase['__RequestVerificationToken'] = token
    dictbase['Cache-Control'] = 'no-cache'
    dictbase['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
    
def grep_csrf(html):
    pat = re.compile(r".*meta name=\"csrf_token\" content=\"(.*)\"", re.I)
    matches = (pat.match(line) for line in html.splitlines())
    return [m.group(1) for m in matches if m]

def login_data(username, password, csrf_token):
    def encrypt(text):
        m = hashlib.sha256()
        m.update(text)
        return base64.b64encode(m.hexdigest())
    password_hash = encrypt(username + encrypt(password) + csrf_token)
    return '<?xml version "1.0" encoding="UTF-8"?><request><Username>%s</Username><Password>%s</Password><password_type>4</password_type></request>' % (username, password_hash)

def set_network(baseurl, session, lte_band, net_mode):
  data = '<request><NetworkMode>%s</NetworkMode><NetworkBand>3FFFFFFF</NetworkBand><LTEBand>%s</LTEBand></request>' % (net_mode, lte_band)
  r = session.request('POST', baseurl + "api/net/net-mode", data=data)
  print r.text

def get_network(baseurl, session):
        r = session.get(baseurl + "api/net/net-mode")
        return r.text

def check_ping():
    hostname = "8.8.8.8"
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        pingstatus = "Network Active"
    else:
        pingstatus = "Network Error"
    return pingstatus

def reconnect(baseurl, username, password):
  print "Network Error. Reconnecting..."
  print "Trying to log in..."
  s = login(baseurl, username, password)
  print "Logged !!"
  r = get_network(baseurl, s)
  print r
  if "800C5" in r:
    print "Setting to 4G only, 2600MHz"
    net_mode = "03"
    lte_band = "40"
  else:
    print "Setting net to 4G+3G, all EU bands"
    net_mode = "00"
    lte_band = "800C5"
  set_network(baseurl, s, lte_band, net_mode)
  r = get_network(baseurl, s)
  print r
  #logoff(baseurl, s)

baseurl = "http://192.168.8.1/"
username = "admin"
password = "password"

if __name__ == "__main__":
  ping_status = check_ping()
  print ping_status
  if (ping_status != "Network Active"):
    reconnect(baseurl, username, password)
    #dhcp(baseurl, s)
