from nfsn import NearlyFreeSpeechService
from webfaction import WebFactionService

services= [WebFactionService, NearlyFreeSpeechService]
services_by_name= dict(((s.__name__,s) for s in services))
