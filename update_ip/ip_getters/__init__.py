import base
import getters
import logging
import time
log= logging.getLogger('update_ip.ip_getters')

ALL_CLASSES= base.BaseIpGetter.__subclasses__()
ALL= [x() for x in ALL_CLASSES]

def get_ip(tries=3, try_delay=15):
    tries= 3
    for i in range(tries):
        try:
            return get_ip_once()
        except base.GetIpFailed:
            if i<tries-1:
                log.debug("Ip getting try {0} failed. Sleeping {1} seconds".format(i, try_delay))
                time.sleep(try_delay)
    raise base.GetIpFailed("Failed to get IP (after {0} tries)".format(tries))

def get_ip_once():
    import random
    getters= ALL[:]
    random.shuffle( getters ) #for load balancing purposes
    for getter in getters:
        log.debug("Getting ip with getter {0}".format(getter.NAME))
        try:
            return getter.get_ip()
        except base.GetIpFailed as e:
            log.info("IpGetter {0} failed to get IP: {1}".format(getter.NAME, e))
    raise base.GetIpFailed("None of the ip_getters returned a good ip")
