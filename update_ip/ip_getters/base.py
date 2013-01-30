import re
import urllib2
import socket

socket.setdefaulttimeout(5)

class GetIpFailed(Exception):
    pass

ip_regex= re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


def get_ip_in_text( text ):
    ips= ip_regex.findall( text )
    if len(ips)==0:
        raise GetIpFailed("Could not get ip from text")
    if len(ips)>1:
        if ips.count(ips[0])!=len(ips): #if not all elements are equal
            raise GetIpFailed("Got multiple ips from text: "+str(ips))
    ip = ips[0]
    try:
        socket.inet_aton(ip)
    except socket.error:
        raise GetIpFailed("IP validation failed: "+ip)
    return ip

def get_ip_from_http( url , change_user_agent=None):
    headers= {} if not change_user_agent else {'User-Agent':change_user_agent}
    request= urllib2.Request(url, headers=headers)
    try:
        page = urllib2.urlopen( request )
        text= page.read()
    except urllib2.URLError:
        raise GetIpFailed("Error fetching page from url: "+url)
    except socket.timeout:
        raise GetIpFailed("Timeout fetching page from url: "+url)
    return get_ip_in_text( text )

class BaseIpGetter(object):
    NAME = 'Base Ip Getter' # Replace this with the name of the IP getter
    def get_ip(self):
        return get_ip_from_http( self.URL )
