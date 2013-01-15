from update_ip.ip_getters.base import BaseIpGetter,  get_ip_from_http


class DynDns(BaseIpGetter):
    NAME= "dyndns.org"
    URL= "http://checkip.dyndns.org"


class IpChicken(BaseIpGetter):
    NAME= "ipchicken.com"
    URL= "http://ipchicken.com/"

class IfconfigMe(BaseIpGetter):
    NAME= "ifconfig.me"
    URL= "http://ifconfig.me/ip"
    
'''
class JsonIp(BaseIpGetter):
    NAME="jsonip.com"
    URL="http://jsonip.com"
'''

