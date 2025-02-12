from pydub import AudioSegment
import sounddevice as sd
import numpy as np

class AudioOut:

    #Dictionary mit Noten
    notes_freq = {
            "C2": {"piano": "samples/C2-Klavier.wav", "frequency": 65.41},
            "D2": {"piano": "samples/D2-Klavier.wav", "frequency": 73.42},
            "E2": {"piano": "samples/E2-Klavier.wav", "frequency": 82.41},
            "F2": {"piano": "samples/F2-Klavier.wav", "frequency": 87.31},
            "G2": {"piano": "samples/G2-Klavier.wav", "frequency": 98.00},
            "A2": {"piano": "samples/A2-Klavier.wav", "frequency": 110},
            "B2": {"piano": "samples/B2-Klavier.wav", "frequency": 123.47},
            "C3": {"piano": "samples/C3-Klavier.wav", "frequency": 130.81},
            "D3": {"piano": "samples/D3-Klavier.wav", "frequency": 146.83},
            "E3": {"piano": "samples/E3-Klavier.wav", "frequency": 164.81},
            "F3": {"piano": "samples/F3-Klavier.wav", "frequency": 174.61},
            "G3": {"piano": "samples/G3-Klavier.wav", "frequency": 196.00},
            "A3": {"piano": "samples/A3-Klavier.wav", "frequency": 220},
            "B3": {"piano": "samples/B3-Klavier.wav", "frequency": 246.94},
            "C4": {"piano": "samples/C4-Klavier.wav", "frequency": 261.63},
            "D4": {"piano": "samples/D4-Klavier.wav", "frequency": 293.67},
            "E4": {"piano": "samples/E4-Klavier.wav", "frequency": 329.63},
            "F4": {"piano": "samples/F4-Klavier.wav", "frequency": 349.23},
            "G4": {"piano": "samples/G4-Klavier.wav", "frequency": 391.00},
            "A4": {"piano": "samples/A4-Klavier.wav", "frequency": 440},
            "B4": {"piano": "samples/B4-Klavier.wav", "frequency": 493.88},
            "C5": {"piano": "samples/C5-Klavier.wav", "frequency": 523.25},
            "D5": {"piano": "samples/D5-Klavier.wav", "frequency": 587.33},
            "E5": {"piano": "samples/E5-Klavier.wav", "frequency": 659.26},
            "F5": {"piano": "samples/F5-Klavier.wav", "frequency": 698.46},
            "G5": {"piano": "samples/G5-Klavier.wav", "frequency": 783.99},
            "A5": {"piano": "samples/A5-Klavier.wav", "frequency": 880},
            "B5": {"piano": "samples/B5-Klavier.wav", "frequency": 987.77},
            "C6": {"piano": "samples/C6-Klavier.wav", "frequency": 1046.5}
        }

    #---------------------------------------------------------------------

    #Konstruktor
    def __init__(self, notes, inst, duration_ms = 1000, chord=True):
        self.notes = notes
        self.inst = inst
        self.chord = chord
        try:
            len(duration_ms)
            if chord == True:
                self.duration_ms = duration_ms[0] #Akkord benötigt nur eine Dauer
            else:
                self.duration_ms = duration_ms 
        except:
            if chord == False:
                self.duration_ms = [duration_ms] * len(notes)   #Melodie benötigt Dauer für jeden Ton                
            else:
                self.duration_ms = duration_ms 

    #---------------------------------------------------------------------

    #Methode zum abspielen eines Tones
    def play(self, safe = False):
        if self.inst == "Piano":
            self.playPiano(safe)
        elif self.inst == "Sine":
            self.playSine()
        else:
            print("No instrument is choosen!")
        return

    #---------------------------------------------------------------------

    #Methode zum Abspielen eines Tones mit Klaviersamples
    def playPiano(self, safe = False):
        
        def load_note(note):
            return AudioSegment.from_file(self.notes_freq[note]["piano"])
        
        #laden der Noten
        if self.chord:  #Akkord
            final_sound = load_note(self.notes[0])[:self.duration_ms] #anlegen des Audiosegments

            for note in self.notes[1:]:                
                final_sound = final_sound.overlay(load_note(note)[:self.duration_ms])

        else:   #Melodie
            final_sound = load_note(self.notes[0])[:self.duration_ms[0]]

            for note,dur in zip(self.notes[1:],self.duration_ms[1:]):
                final_sound += load_note(note)[:dur]              
        
        if safe:
            output_datei = "tonfolge.wav"
            final_sound.export(output_datei, format="wav")

        #AudioSegment in numpy-Array konvertieren, so dass es mit sounddevice ausgegeben werden kann
        samples = np.array(final_sound.get_array_of_samples(), dtype=np.float32)  

        #normieren
        samples = samples / (2**15)  #Normiere auf [-1, 1] oder Teilen durch (2**15)
                                     #Dies geht, da die vorher verwendeten Int-werte 16 Bit groß sind
        samplerate = final_sound.frame_rate

        sd.play(samples, samplerate)
        sd.wait()

        return

    #---------------------------------------------------------------------

    #Methode zum abspielen eines Tones als Sinus
    def playSine(self):

        samplerate = 44100  #Abtastrate in Hz

        #Abspielen des Akkords
        if self.chord == True:

            duration = self.duration_ms/1000                       #Dauer des Tons in Sekunden  
                      
            t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
            tone = np.zeros(len(t))      #kombinierter Ton

            for i in self.notes:
                sin = 0.5*np.sin(2 * np.pi * self.notes_freq[i]["frequency"] * t)  # Sinusschwingungen erstellen
                tone += sin

            # Normierung des sins zum Bereich -1...1
            tone /= 2* np.max(np.abs(tone))
            
            sd.play(tone, samplerate)  #Ton abspielen
            sd.wait()

        #Abspielen der Melodie    
        else:
            for i,dur in zip(self.notes,self.duration_ms):
                duration = dur/1000  #Dauer des Tons in Sekunden
                
                t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
         
                sin = 0.5*np.sin(2 * np.pi * self.notes_freq[i]["frequency"] * t)
                
                sd.play(sin, samplerate)
                sd.wait()        
        return

#===================================================================================================

def valsToMs(vals, bpm = 120):
    duration = 60/bpm * 4 * 1000   #Länge eines Taktes in ms
    
    valsMs = [0] * len(vals)

    for i in range(len(vals)):
        valsMs[i] = duration / vals[i]
    return valsMs