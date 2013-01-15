import base
import getters

ALL_CLASSES= base.BaseIpGetter.__subclasses__()
ALL= [x() for x in ALL_CLASSES]

def get_ip():
    import random
    remaining= ALL[:]
    while remaining:
        getter= random.choice(remaining)
        try:
            return getter.get_ip()
        except base.GetIpFailed:
            remaining.remove( getter )
    raise base.GetIpFailed("None of the ip_getters returned a good ip")
