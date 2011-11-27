from update_ip.ip_getters.base import BaseIpGetter,  get_ip_from_http

class DynDns(BaseIpGetter):
    NAME= "dyndns.org"
    URL= "http://checkip.dyndns.org"
    def get_ip(self):
        return get_ip_from_http( self.URL )
