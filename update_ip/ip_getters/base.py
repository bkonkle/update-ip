import re
import urllib2
import socket

socket.setdefaulttimeout(5)

class GetIpFailed(Exception):
    pass

ip_regex= re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

def _is_valid_ip(ip_str):
    try:
        socket.inet_aton(ip_str)
        return True
    except socket.error:
        return False


def get_ip_in_text( text ):
    ips= ip_regex.findall( text )
    valid_ips = filter(_is_valid_ip, ips)
    if len(valid_ips)==0:
        raise GetIpFailed("Could not get ip from text")
    if len(set(valid_ips)) > 1:
        raise GetIpFailed("Got multiple ips from text: "+str(valid_ips))
    ip = valid_ips[0]
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
