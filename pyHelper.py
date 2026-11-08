import re
import os
import pyttsx3
from faster_whisper import WhisperModel
import queue
import threading
import sounddevice
import time
import numpy

#place module imports here
import weather
import fileOpener
import music
import httpBrowser
import geminiBrowser
import sandwich
import whereIs
import runModule

class captions:
    def __init__(self):
        self.busy = False
        # WHISPER CONFIG
        self.SR_MODEL = "tiny.en"
        self.SR_SAMP_RATE = 16000
        self.SR_CHANNELS = 1
        self.SR_SEND_2_BOT = 0.5
        
        # Queues and stuff
        self.sr_queue = queue.Queue()
        self.mic_incoming = queue.Queue()
        self.say_queue = queue.Queue()
        self.init_sr()
    
    def init_sr(self):
        # Starts main threads
        threading.Thread(target=self.sr_worker,daemon=True).start()
        threading.Thread(target=self.mic_listener,daemon=True).start()

    def sr_worker(self):
        model = WhisperModel(self.SR_MODEL, device="cpu", compute_type="int8")
        while True:
            #epic loop dun dun duuuuuuuuuuuunnnnnnnnnnnn
            try:
                audio_data = self.sr_queue.get(timeout=1)
                segments, _ = model.transcribe(audio_data, beam_size=5)
                full_text = "".join([segment.text for segment in segments]).strip()
                if full_text:
                    self.say_queue.put(full_text)
            except Exception:
                pass
    
    def do_mic_stuff(self, indata, frames, info_time, status):
        self.mic_incoming.put(indata.copy())

    def mic_listener(self): # the only one who listens to yapping miceal
        a_buff = []
        s_start_time = None
        is_recording = False
        stream = sounddevice.InputStream(samplerate=self.SR_SAMP_RATE, channels=self.SR_CHANNELS, callback=self.do_mic_stuff)
        with stream:
            calibration_start = time.time()
            calibration_rms_values = []

            while time.time() - calibration_start < 2:
                try:
                    chunk = self.mic_incoming.get(timeout=0.1)
                    rms = numpy.sqrt(numpy.mean(chunk**2))
                    calibration_rms_values.append(rms)
                except queue.Empty:
                    continue

            if calibration_rms_values:
                avg_noise_floor = numpy.mean(calibration_rms_values)
                SILENCE_THRESHOLD = max(avg_noise_floor + 0.005, 0.01) 
            else:
                SILENCE_THRESHOLD = 0.01 # Fallback if queue failed

            print(f"Room noise = {SILENCE_THRESHOLD}")
            while True:
                try: # if he fails we dont care
                    chunk = self.mic_incoming.get(timeout = 0.1)
                    if self.busy:
                        a_buff.clear()
                        is_recording = False
                        s_start_time = None
                        continue

                    a_buff.append(chunk)
                    rms = numpy.sqrt(numpy.mean(chunk**2))

                    if rms > SILENCE_THRESHOLD:
                        s_start_time = None # hasn't changed yet...
                        is_recording = True
                    else:
                        if is_recording and s_start_time is None:
                            s_start_time = time.time()
                    
                    if is_recording and s_start_time:
                        if time.time() - s_start_time >= self.SR_SEND_2_BOT:
                            full_audio = numpy.concatenate(a_buff, axis=0).flatten()
                            self.sr_queue.put(full_audio)
                            a_buff.clear()
                            is_recording = False
                            s_start_time = None

                
                except Exception:
                    pass


def pyHelperMain():
	stt = captions()
	#type importName.moduleName() as an element in the array to be able to use the module
	modules = [weather.WeatherModule(), fileOpener.FileOpenerModule(), music.MusicModule(), httpBrowser.HttpModule(), geminiBrowser.GeminiModule(), sandwich.SandwichModule(), whereIs.WhereIsModule(), runModule.RunModule()]
	
	inp = ""
	while True:
		print("pyHelper ~ ", end="")
		inp = str(input())
		if inp.strip() == "": #Ignore blank lines
			continue
		if inp[0] == "!": #Forward !command to system shell
			os.system(inp[1:])
			continue
		inp = inp.lower()
		if inp in ["exit", "quit", "bye", "x", "q"]: #Exiting
			break;
		if inp in ["help", "?"]: #Help menu
			print("pyHelper: an attempt at making a modular terminal voice assistant")
			print("\nType exit, quit, bye, x, or q to exit\nType clear, c, or cls to clear screen\nStart prompt with ! to forward to shell")
			if len(modules) > 0:
				print("\nInstalled modules:")
				mods = ""
				for module in modules:
					mods += module.getName() + ", "
				mods = mods[0:len(mods) - 2]
				print(mods)
		elif inp in ["clear", "c", "cls"]: #Screen clearing
			os.system("clear")
		elif len(modules) == 0: #No modules error
			print("No modules installed.")
		else: #Calling modules based on input
			bestModule = None
			bestModuleScore = 0
			genericModuleFound = False
			genericModule = None
			
			for modObj in modules: #Look at all installed modules
				if modObj.isGeneric() and not genericModuleFound: #If generic module, remember that
					genericModule = modObj
					genericModuleFound = True;
				
				matchCount = 0
				for kw in modObj.getKeywords(): #Count matching keywords
					if re.sub("[^a-zA-Z0-9 ]", "", kw).lower() in re.sub("[^a-zA-Z0-9 ]", "", inp).lower():
						matchCount += 1
				if matchCount > bestModuleScore: #Maximize matching keywords and store best module
					bestModuleScore = matchCount
					bestModule = modObj
			
			if bestModuleScore > 0: #If a module is found, run it
				bestModule.run(inp)
			elif genericModuleFound == True: #Else, run a generic module if available
				genericModule.run(inp)
			else: #Else, complain to user
				print("No appropriate module found.")

if __name__ == "__main__":
	pyHelperMain()
