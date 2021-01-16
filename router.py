#!/usr/bin/python3

"""
2021 @fernand0
Based on the 
2020 @MrHctr project.
https://github.com/hcordobes/mitra_reset

Exención de responsabilidad
  Se proporciona sin garantía *de ningún tipo*, no se aceptan
  responsabilidades por uso *EN NINGÚN CASO*

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import requests
import base64
import re

from bs4 import BeautifulSoup
import keyring
import getpass

def reboot(host, session):
    # Not tested
    result = requests.get(host + 'resetrouter.html', cookies=session)
    # Extract "var sessionKey='nnnn'"
    
    match = re.search(r"var sessionKey='([0-9]+)'", result.text)
    sessionKey = match.group(1)
    params = {'sessionKey':sessionKey}
    result = requests.get(host + 'rebootinfo.cgi', params=params, cookies=session)

def listIPs(host, session):
    result = requests.get(host + 'networkmap.html',  cookies=session)
    soup = BeautifulSoup(result.content, features="lxml")
    imgs = soup.find_all('img')
    listIPs = {}
    # We are using a dict because there were some duplicates
    
    for img in imgs:
        oc = img.get('onclick')
        if oc and (oc.find('showElement')>=0): 
            data = eval(oc[11:-1])
            listIPs[data[2]] = data
    
    for ip in listIPs:
        print(f"Name: {listIPs[ip][0]}. IP: {listIPs[ip][2]}")
 
def getCredentials(ip):
    
    ####################
    user = '1234'
    password = keyring.get_password(ip, user)
    if not password:
        password = getpass.getpass()
        keyring.set_password(ip, user, password)
    
    host = 'http://' + ip + '/'
    auth = user + ':' + password
    sessionKey = base64.b64encode(auth.encode())
    data = {'sessionKey': sessionKey, 'pass':''}
    r = requests.post(host + 'login-login.cgi', data=data)
    
    # Get cookies (interested in SESSION)
    session = r.cookies
    
    return session 
 

def main():
    ####################
    # Change this
    ip='192.168.1.1'
    host = f'http://{ip}/'

    session = getCredentials(ip)

    if (len(sys.argv) > 1) and (sys.argv[1] == '-r'):
        reboot()
    else: 
        listIPs(host, session)
        
if __name__ == '__main__':
    main()
