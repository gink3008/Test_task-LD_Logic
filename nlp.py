from asyncio import InvalidStateError
from email.policy import Policy
from config import nn, nv, configs, promt_txt, msisdn, phonenumber
import time


#case hello_logic
class hello_logic():
    to_main_logic = False
    to_hangup = False
    def __init__(self, r):
        self.hello(r)
        self.check_entities(r)
        self.main_logic = main_logic(r)
        self.hangup = hangup()

    def hello(self, r):
        nv.say(promt_txt["hello"]["say"])

    def hello_null(self,r):
        nv.say(promt_txt['hello']['hello_null'])

    def hello_repeat(self, r):
        nv.say(promt_txt['hello']['hello_repeat'])
        self.check_entities(r)

    def check_entities(self, r):
        if r.has_entities() and r.has_intents():
            if r.intent("confirm"):
                self.main_logic.recommend_main(r)
            if r.intent("wrong_time"):
                self.hangup.hangup_wrong_time()
            if r.intent("repeat"):
                self.hello_repeat(r)
            
        if r.utterance == None:
            self.hello_null(r)
            self.hangup.hangup_null(r)
        
        if r.utterance != None and not r.has_intents() :
            self.main_logic.recommend_main()
    

#case main_logic
class main_logic():
    def __init__(self):
        self.hangup = hangup()
        self.forward = forward_logic(phonenumber)

    def recommend_main(self, r):
        nv.say(promt_txt['main']['say'])
        self.check_answer(self, r)

    def check_answer(self, r):
        if r.has_entities() and r.has_intents():
            if r.intent("recommendation_score") in range(0,9):
                self.hangup.hangup_negative(r)

            if r.intent("recommendation_score") in range(0,9):
                self.hangup.hangup_positive(r)

            if r.intent("recommendation")=="negative":
                self.recommend_score_negative(r)

            if r.intent("recommendation")=="neutral":
                self.recommend_score_neutral(r)

            if r.intent("recommendation")=="positive":
                self.recommend_score_positive(r)
            
            if r.intent("recommendation")=="dont_know":
                self.recommend_repeat_2(r)
            
            if r.intent("wrong_time"):
                self.hangup_wrong_time()

            if r.intent("question"):
                self.forward.forward()

        if r.utterance == None:
            self.recommend_null(r)
            self.hangup["null"] = True
            self.hangup.hangup_null(r)
        
        if r.utterance !=None and not r.has_intents() :
            self.main_logic.recommend_main()
        
    def recommend_null(self, r):
        nv.say(promt_txt['main']['recommend_null'])
    
    def recommend_default(self, r):
        nv.say(promt_txt['main']['recommend_default'])
        self.check_answer(r)


    def recommend_repeat(self, r):
        nv.say(promt_txt['main']['say'])
        self.check_answer(r)

    def recommend_repeat_2(self, r):
        nv.say(promt_txt['main']['recommend_repeat_2'])
        self.check_answer(r)

    def recommend_score_negative(self, r):
        nv.say(promt_txt['main']['recommend_score_negative'])
        self.check_answer(r)

    def recommend_score_positive(self, r):
        nv.say(promt_txt['main']['recommend_score_positive'])
        self.check_answer(r)

    def recommend_score_neutral(self, r):
        nv.say(promt_txt['main']['recommend_score_neutral'])
        self.check_answer(r)

    def hangup_wrong_time(self):
        self.hangup_wrong_time()


#case hangup_logic
class hangup():
    def hangup_null():
        nv.say(promt_txt["hangup"]['hangup_null'])
        nv.hangup()

    def hangup_negative():
        nv.say(promt_txt["hangup"]['hangup_negative'])
        nv.hangup()

    def hangup_positive():
        nv.say(promt_txt["hangup"]['hangup_positive'])
        nv.hangup()

    def hangup_wrong_time():
        nv.say(promt_txt["hangup"]['hangup_wrong_time'])
        nv.hangup()


        
#case forward_logic
class forward_logic():
    def __init__(self, phonenumber):
        self.phonumber = phonenumber

    def forward(self):
        def abonent_alive():
            nn.log('HCSTATUS_1',f"abonent alive {nn.env('HCSTATUS_1')}")
            if nn.env ('HCSTATUS_1') == 'the subscriber dropped before connecting':
                nv.synthesize('the subscriber dropped before connecting')
                return False
            return True

        def operator():
            try:
                if not abonent_alive():
                    nn.log("hangup after first abonent alive")
                    nv.hangup()
                nn.log('---- test second call ----')
                nn.env('HCSTATUS_2', 'a call is taken by an operator')
                if not abonent_alive():
                    nn.log("hangup after first abonent alive")
                    nv.hangup()
                nv.set_default('listen', no_input_timeout=4000, recognition_timeout=30000,speech_complete_timeout=2500, asr_complete_timeout=2500)
                nv.say('playback')
                if not abonent_alive():
                    nn.log("hangup after second abonent alive")
                    nv.hangup()
                nn.env('HCSTATUS_2', 'connection')
                nv.bridge_to_caller()
                nn.log('duration_hc', nv.get_call_duration())
                nn.log('call_transcript_hc', nv.get_call_transcription(return_format=nv.TRANSCRIPTION_FORMAT_TXT))
                nn.dump()

            except InvalidCallStateError:
                print("operator InvalidCallStateError")
            except Exception as e:
                nn.log(f'---- second call exception {e} ----')

        nv.hold_and_call(self.phonenumber, entry_point=operator)
        time.sleep(15)

        try:
            nv.wait_for_second_call()
            print("after wait for second call")
            nv.synthesize('all operators are busy')
            nn.env('status', '10000')
            nn.log('status', '10000')
            nn.env('reason', 'no_reason')

        except InvalidCallStateError as error:
            print("main online InvalidCallStateError")
            nn.env('HCSTATUS_1', 'the subscriber dropped before connecting')
            nn.log('HCSTATUS_1', 'the subscriber dropped before connecting')
            if nn.env('HCSTATUS_2') == 'connection':
                nn.env('reason', 'all_ok')
                nn.log('---- all okey ----')
                nn.dump()

            elif nn.env('HCSTATUS_2') == 'a call is taken by an operator':
                nn.log('---- abonent hangup ----')
                nn.env('reason', 'abonent_reject')
                nn.dump()

        except Exception as e:
            print("main online Exception")
            nn.log(str(e))

    


def __main__ ():
    configs()
    nn.call(msisdn, entry_point="main", use_default_prefix=True)
    with nv.listen((None, 500)) as r:
        nv.random_sound(2000, 7000)
        start = hello_logic()
        start.hello(r)

    