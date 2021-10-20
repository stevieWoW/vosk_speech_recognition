import argparse
import os
import queue
import sys
import json
import sounddevice as sd
import vosk
import threading
import time

q = queue.Queue()

class Activities:
    def licht(GPIO):
        print(f" Schalte das Licht an mit {GPIO}")
    
    def tor(GPIO):
        print(f" Schalte das Tor an mit {GPIO}")


class speech: 
    STARTCODE = 'computer'
    def __init__(self,startcode):
        self.STARTCODE = startcode

    def thread_timer(self):
        self.power_gpio(25)
        time.sleep(10)
        self.close_gpio(25)
        

    def active(self,rec):
        print("active")
        t = threading.Thread(target=self.thread_timer)
        t.start()
        i=0
        while t.is_alive():
            print(i)
            data = q.get()
            if rec.AcceptWaveform(data):
                print("second record")
                res = json.loads(rec.Result())
                if 'LICHT'.upper() in res['text'].upper():
                    Activities.licht(26)

                elif 'Tor'.upper() in res['text'].upper():
                    Activities.tor(26)
                print(res['text'])
            i+=1


    def power_gpio(self,GPIO):
        print(f"Power {GPIO}")
    
    def close_gpio(self,GPIO):
        print(f"Close {GPIO}")
    


    

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


parser = argparse.ArgumentParser(add_help=True)
parser.add_argument(
    '-m','--model', type=str, nargs='?',default='model', help='Pfad zum Model'
)
parser.add_argument(
    '-d','--device', type=str,nargs='?',default='0,0',help='Eingabegerät(Mikrofon als String)'
)
parser.add_argument(
    '-r','--samplerate',type=int,nargs='?', default=16000,help='Sample Rate'
)

args = parser.parse_args('')

if not os.path.exists(args.model):
    print("Please download a model from https://alphacephei.com/vosk/models and unpack to 'model'")
    #exit(1)

model = vosk.Model(args.model)

speech = speech('computer')

with sd.RawInputStream(samplerate=args.samplerate, blocksize=8000, device=args.device,dtype='int16',
                        channels=1, callback=callback):
    print('*' * 80)
    rec = vosk.KaldiRecognizer(model, args.samplerate)
    while True:
        data = q.get()
        print("start to speak")
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if speech.STARTCODE == res['text']:
                speech.active(rec)

        else:
            pass
            #print(rec.PartialResult())
