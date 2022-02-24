import NeuroNetLibrary
import NeuroNluLibrary
import NeuroVoiceLibrary
import json

nn = NeuroNetLibrary (nlu_call, event_loop)
nlu  = NeuroNluLibrary(nlu_call, event_loop)
nv = NeuroVoiceLibrary(nlu_call, loop)
phonenumber = ""

msisdn = nn.dialog.msisdn
def promt_txt():
    with open("./promt_txt.json", 'r') as f:
        promt_txt = json.load(f)
    return promt_txt

def configs():
    nn.env('flag', 'vova')
    lang = nn.env('ru-RU')
    if lang:
        nv.media_params('lang', lang)

def headers():
    token = nn.storage('middleware_token')
    headers = {'Authorization': 'Bearer ' + token}
    return headers
