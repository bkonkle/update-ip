from update_ip.ip_getters.base import BaseIpGetter,  get_ip_from_http

class WhatIsMyIp(BaseIpGetter):
    NAME= "whatismyip.com"
    URL= "http://automation.whatismyip.com/n09230945.asp"
    def get_ip(self):
        return get_ip_from_http( self.URL )
