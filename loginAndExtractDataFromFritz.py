#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#######################################################################################################################
#
#    Python prototype which logs on to a Fritz AVM 7390 and 
#    extracts the number of sent and received bytes of 
#    today, yesterday, last week and last month
#
#    Visit https://github.com/framps/pythonScriptCollection for latest code and other details
#
#######################################################################################################################
#
#    Copyright (C) 2013 framp at linux-tips-and-tricks dot de
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################################################################

import httplib
from xml.dom import minidom
import hashlib
import re
import sys

USER_AGENT="Mozilla/5.0 (U; Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0"

def getPage(server, sid, page, port=80):
    
    conn = httplib.HTTPConnection(server+':'+str(port))
    
    headers = { "Accept" : "application/xml",
                "Content-Type" : "text/plain",
                "User-Agent" : USER_AGENT}

    pageWithSid=page+"?sid="+sid
    conn.request("GET", pageWithSid, '', headers)
    response = conn.getresponse()    
    data = response.read()
    if response.status != 200:
        print "%s %s" % (response.status, response.reason)
        print data 
        sys.exit(0)
    else:
        return data

def loginToServer(server,password,port=80):
    
    conn = httplib.HTTPConnection(server+':'+str(port))
    
    headers = { "Accept" : "application/xml",
                "Content-Type" : "text/plain",
                "User-Agent" : USER_AGENT}

    initialPage='/login_sid.lua'
    conn.request("GET", initialPage, '', headers)
    response = conn.getresponse()    
    data = response.read()
    if response.status != 200:
        print "%s %s" % (response.status, response.reason)
        print data
        sys.exit(0)
    else:
        theXml = minidom.parseString(data)
        sidInfo = theXml.getElementsByTagName('SID')
        sid=sidInfo[0].firstChild.data
        if sid == "0000000000000000":
            challengeInfo = theXml.getElementsByTagName('Challenge')
            challenge=challengeInfo[0].firstChild.data
            challenge_bf = (challenge + '-' + password).decode('iso-8859-1').encode('utf-16le')
            m = hashlib.md5()
            m.update(challenge_bf)
            response_bf = challenge + '-' + m.hexdigest().lower()
        else:
            return sid
                                        
    headers = { "Accept" : "text/html,application/xhtml+xml,application/xml",
                "Content-Type" : "application/x-www-form-urlencoded",
                "User-Agent" : USER_AGENT}

    loginPage="/login_sid.lua?&response=" + response_bf
    conn.request("GET", loginPage, '', headers)    
    response = conn.getresponse()    
    data = response.read()    
    if response.status != 200:
        print "%s %s" % (response.status, response.reason)    
        print data
        sys.exit(0)
    else:
        sid = re.search('<SID>(.*?)</SID>', data).group(1)
        if sid == "0000000000000000":
            print "ERROR - No SID received because of invalid password"
            sys.exit(0)
        return sid            

server='192.168.178.1'
password='geheim'

sid=loginToServer(server,password)

if not sid:
    print "ERROR logging on"
    sys.exit(0)

page=getPage(server,sid,"/internet/inetstat_counter.lua")

for line in page.split('\n'):
    if '["inetstat' in line:
        match = re.search('.*\/(.*?)\/(.*?)".*=.*"(.*?)"', line)
        if match:
            print match.group(1) + " " + match.group(2) + " " + match.group(3)  
