import json
import requests
import zipfile
import os
import uuid
from urllib.parse import urlparse

class WebProxy():
    def __init__(self):
        self.params          = self.get_from_big("SHADERIOPROXYLIST")
        self.ip              = self.params['host']
        self.port            = self.params['port']
        self.user            = self.params['user']
        self.psw             = self.params['psw']
        self.type            = self.params['type']
        
        self.current = ''
        
    def get_plugin(self):
        return self._create_plugin()

    def get_from_big(self, proxyDomain):
        PROXY_API = "https://bigboost.bigdatacorp.com.br/ProxiesAPI/api/BDCProxiesListServer?key=13FE584A-C637-43CB-AE1F-9E3E4B3F6F99&provider={0}&function=GetProxy&zone=srf"

        req = requests.get(PROXY_API.format(proxyDomain))
        
        response = json.loads(req.text)
        if not (response['errormessage']):
            proxy = {
                "host" : response['ip'],
                "port" : response['port'],
                "user" : response['user'],
                "psw"  : response['psw']
            }
            if(response['sslsupport']):
                proxy['type'] = "http"
            else:
                proxy['type'] = "http"
            #print(proxy)
            return proxy
        return False

    def __str__(self):
        return 'http://{0}:{1}@{2}:{3}/'.format(self.user, self.psw, self.ip, self.port)

    def _create_plugin(self):
        self.current = str(uuid.UUID(bytes=os.urandom(16), version=4)) + '.zip'
        pluginfile   = os.path.join(os.getcwd(), 'temp_proxies', self.current)

        with zipfile.ZipFile(pluginfile, 'w') as zp, open("proxy_extension/manifest.json", "r") as manifest_json, open("proxy_extension/background.js", "r") as background_js:
            bg = background_js.read()
            bg = bg.replace("xTYPEx", self.type)
            bg = bg.replace("xPORTx", self.port)
            bg = bg.replace("xHOSTx", self.ip)
            bg = bg.replace("xUSERx", self.user)
            bg = bg.replace("xPSWDx", self.psw)
            bg = bg.replace("xDOMAINx", "")
            
            zp.writestr("manifest.json", str(manifest_json.read()))
            zp.writestr("background.js", bg)
        #print(pluginfile)
        return pluginfile

    def destroy(self):
        os.remove(os.path.join('temp_proxies', self.current))
        self.current = ""