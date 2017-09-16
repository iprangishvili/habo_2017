# import requests
# from requests.auth import HTTPDigestAuth
# from multiprocessing import Pool
# from functools import partial

# def moveRobot(arm,action):
#     auth=HTTPDigestAuth('Default User', 'robotics')
#     url = 'http://104.46.57.187/rw'
#     # url = 'http://104.45.14.152/rw'
#     r0=requests.get(url,auth=auth)
#   #  print(r0.text)
#     r1 = requests.post(url + '/rapid/symbol/data/RAPID/'+arm+'/Remote/'+'stName'+'?action=set',data={'value': '"' + action + '"'}, auth=HTTPDigestAuth('Default User', 'robotics'))
#     print(r1)
#     print(r1.text)
#     r2 = requests.post(url + '/rapid/symbol/data/RAPID/'+arm+'/Remote/bStart?action=set',data={'value':'true'},auth=HTTPDigestAuth('Default User', 'robotics'))
#     print(r2)
#     # r1.close()
#     # r2.close()
#     return;

# p = Pool(2)
# p.map(partial(moveRobot, action='Surprised'), ['T_ROB_L', 'T_ROB_R'])
# # moveRobot('T_ROB_R','SayNo')
# # moveRobot('T_ROB_R', 'Contempt')

import sys, json
import requests
from requests.auth import HTTPDigestAuth
import urllib
import time
from threading import Thread
import httplib, urllib, base64
from luis_sdk import LUISClient


# headers = {"Ocp-Apim-Subscription-Key": apiKey}

# url = 'http://104.46.57.187/rw'
url = 'http://192.168.125.1/rw'
# url = 'http://104.45.14.152/rw'


auth = HTTPDigestAuth('Default User', 'robotics')

session = requests.session()
globalaction = ''

# Get authenticated
r0 = session.get(url + '/rapid/symbol/data/RAPID/'+'T_ROB_R'+'/Remote/bStart?json=1',
                   auth=auth)
assert(r0.status_code == 200)
#print(r0.json()['_embedded']['_state'][0]['value'])


def check(arm, variable):
    r = session.get(url + '/rapid/symbol/data/RAPID/'+arm+'/Remote/'+variable+'?json=1')
    assert(r.status_code == 200)
    return r.json()['_embedded']['_state'][0]['value']

def checkBool(arm, variable):
    return True if check(arm, variable) == "TRUE" else False

def setString(arm, variable, text):
    payload={'value':'"'+text+'"'}
    r = session.post(url + '/rapid/symbol/data/RAPID/'+arm+'/Remote/'+variable+'?action=set',
                     data=payload)
    print(r)
    print(r.text)
    assert(r.status_code == 204)
    return r

def setBool(arm, variable, state):
    payload={'value': 'true' if state else 'false' }
    r = session.post(url + '/rapid/symbol/data/RAPID/'+arm+'/Remote/'+variable+'?action=set',
                     data=payload)
    print(r)
    print(r.text)
    assert(r.status_code == 204)
    return r

def moveRobot(arm,action):
    # print("RUNNING:" + check(arm, 'bRunning'))

    setString(arm, 'stName', action)

    # print("bStart:" + check(arm, 'bStart'))

    setBool(arm, 'bStart', True);

    # print("bStart:" + check(arm, 'bStart'))
    time.sleep(0.5)

    running = checkBool(arm, 'bRunning')
    while running:
        running = checkBool(arm, 'bRunning')
        # print("RUNNING:" + str(running))
        time.sleep(0.4)


    return;



# the trick seems to be to run both arms in parallel because of the
# waitAsyncTask directive in the RAPID code
class otherArm(Thread):
    def run(self):
        moveRobot('T_ROB_L', 'Happy')

# other = otherArm()
# other.run()
# moveRobot('T_ROB_R','SayHello') #Hello
# moveRobot('T_ROB_R','We') #We
# moveRobot('T_ROB_R','Here') #Here
# moveRobot('T_ROB_R','Help') #Help
# moveRobot('T_ROB_R','Kiss') #Thank you
# moveRobot('T_ROB_R','Watch') #watching
# moveRobot('T_ROB_R','Presentation') #Presentation


def process_res(res):
    '''
    A function that processes the luis_response object and prints info from it.
    :param res: A LUISResponse object containing the response data.
    :return: None
    '''
    print(u'---------------------------------------------')
    print(u'LUIS Response: ')
    print(u'Query: ' + res.get_query())
    print(u'Top Scoring Intent: ' + res.get_top_intent().get_name())
    intent_array = res.get_top_intent().get_name().split()

    if res.get_dialog() is not None:
        if res.get_dialog().get_prompt() is None:
            print(u'Dialog Prompt: None')
        else:
            print(u'Dialog Prompt: ' + res.get_dialog().get_prompt())
        if res.get_dialog().get_parameter_name() is None:
            print(u'Dialog Parameter: None')
        else:
            print('Dialog Parameter Name: ' + res.get_dialog().get_parameter_name())
        print(u'Dialog Status: ' + res.get_dialog().get_status())
    print(u'Entities:')
    for entity in res.get_entities():
        print(u'"%s":' % entity.get_name())
        print(u'Type: %s, Score: %s' % (entity.get_type(), entity.get_score()))
    return intent_array

def preprocess(input_text):
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': '{49a3e79bc72f414db090cd8a2eeddc03}',
    }

    APPID = "cf321ffa-6919-4306-9ff1-2ec8fc81328c"
    APPKEY = "49a3e79bc72f414db090cd8a2eeddc03"
    TEXT = input_text
    CLIENT = LUISClient(APPID, APPKEY, True)
    res = CLIENT.predict(TEXT)
    while res.get_dialog() is not None and not res.get_dialog().is_finished():
        TEXT = raw_input(u'%s\n'%res.get_dialog().get_prompt())
        res = CLIENT.reply(TEXT, res)
    return process_res(res)


    # while res.get_dialog() is not None and not res.get_dialog().is_finished():
    #     print (res.get_ent())


if __name__ == "__main__":
    input_text = sys.argv[1]
    # main(action)
    arm = 'T_ROB_R'
    intent_array = preprocess(input_text)
    for i in intent_array:
        moveRobot(arm, i)
