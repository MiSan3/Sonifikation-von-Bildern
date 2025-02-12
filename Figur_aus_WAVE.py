import sounddevice as sd
import os
import functools
import math
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from scipy.interpolate import make_interp_spline
#from sympy import factorint

cDur = [[132,148.5,165,176,198,220,247.5,264,297,330,352,396,440,495,528], #Frequenzen der C-Dur Tonleiter
        [128,140,  156,171,187,209,234,  256,281,314,341,374,418,468,517]] #Grenze ab der aufgerundet wird

#========================================Funktionen========================================

#Funktion nimmt die ersten numFreq unterschiedlichen Frequenzen des Arrays mappt sie auf ganze 
#Töne der C-Dur Tonleiter und erstellt die komplexen Zeiger dazu
def createComplexPointers(freqSorted, animation, aniType):
    
    freq = np.empty((2,numFreq))
    
    #mappen der ersten numfreq Frequenzen auf die normierten Frequenzen
    count = 0
    i = 0

    #normiere so viele Frequenzen bis numFreq verschiedene Frequenzen gefunden wurden
    while i < numFreq:
        f = freqSorted[count][2]
        if f == 0:
            count += 1
            continue       

        for j in range(len(cDur[0])):
            if f <= cDur[1][j]:     #ist Frequenz kleiner als Grenze, dann wird abgerundet
                if j == 0:
                    j = 1
                f = cDur[0][j-1]
                break

        if np.any(freq[0] == f):    #falls die Frequenz schon existiert
            count += 1
            continue       

        freq[0,i] = f                #Frequenz
        freq[1,i] = freqSorted[i][1] #Amplitude
        i += 1

    #Sortieren
    indices = np.argsort(freq[0,:]) #gibt Indizes des sortierten Arrays aus
    freq = freq[:, indices] #ändert die Reihenfolge der Spalten anhand der indizes

    print("--------Frequenzen-und-Auprägung--------")
    print(freq)

    #berechenen des größten gemeinsamen Teilers
    div = functools.reduce(math.gcd, freq[0,:].astype(int))

    rotations = freq[0,0]/div
    tLen = tLen = 1/freq[0][0] * rotations

    time = np.linspace(0.0, tLen, numSamples, endpoint=True)
    
    real = np.empty((0, numSamples))
    imag = np.empty((0, numSamples)) 

    for i in range(numFreq):
        z = freq[1,i] * np.exp(-1j * freq[0,i] * 2.0*np.pi * time) #komplexe Zeiger
        z_real = [j.real for j in z]
        z_imag = [j.imag for j in z]
        real = np.vstack((real,z_real))
        imag = np.vstack((imag,z_imag))

    #Liste für die Spaltensummen erstellen
    row = len(imag)
    collumn = len(imag[0])
    zImag = [0] * collumn
    zReal = [0] * collumn

    #für jede Spalte die Werte der Zeilen zusammenzählen
    for i in range(collumn):
        for j in range(row):
            zImag[i] += imag[j][i]
            zReal[i] += real[j][i]

    if animation:
        if aniType == "Artist":
            createArtistAnimation(imag, real, zImag, zReal)
        elif aniType == "Func":
            createFuncAnimation(zImag, zReal)
    else:
        createPicture(zImag, zReal)

    return 0

#--------------------------------------------------------------------------
#Funktion die das entstehende Bild auf einmal plottet
def createPicture(zImag, zReal):
    fig, ax = plt.subplots()
    
    #erstellen der Splines durch die Datenpunkte
    t = np.arange(len(zImag))
    spline_x = make_interp_spline(t, zReal, bc_type= 'periodic')
    spline_y = make_interp_spline(t, zImag, bc_type= 'periodic')

    #auswerten der Splines mit einer höheren Auflösung und anschließend plotten
    t_new = np.linspace(t.min(), t.max(), len(zImag) * 300)
    x_smooth = spline_x(t_new)
    y_smooth = spline_y(t_new)

    plt.plot(x_smooth, y_smooth, color='red')  #Spline
    plt.scatter(zReal[:], zImag[:])            #zeichnen aller Punkte        
    plt.xlabel("Re", fontsize=14)  
    plt.ylabel("Im", fontsize=14) 
    plt.tick_params(axis='both', labelsize=12)
    ax.set_aspect('equal')

    plt.show()

    return 0

#--------------------------------------------------------------------------
def createArtistAnimation(imag, real, zImag, zReal):

    fig, ax = plt.subplots()
    
    #Erstellen der Artists
    ims = []
    for frame in range(numSamples):
        artist = ax.plot()
        artist.append(ax.scatter(zReal[:frame], zImag[:frame], color='blue'))
        for i in range(len(imag)):
            if i == 0:
                vec = ax.quiver(0, 0, real[i, frame], imag[i, frame], angles='xy', scale_units='xy', scale=1, color='r') #zeichnen des Vektors
            else:
                vec = ax.quiver(np.sum(real[:i, frame]), np.sum(imag[:i, frame]), real[i, frame], imag[i, frame], angles='xy', scale_units='xy', scale=1, color='r')
            artist.append(vec)

        ims.append(artist)

    #Fertige Figur bleibt kurz stehen
    for _ in range(20):  
        ims.append(ims[-1])

    #erstellen der Animation
    im_ani = animation.ArtistAnimation(fig, ims, interval=50, repeat_delay=2000, blit=True)
    ax.set_aspect('equal')
    plt.xlabel("Re", fontsize=14)  
    plt.ylabel("Im", fontsize=14)
    plt.tick_params(axis='both', labelsize=12)
    plt.show()

    return 0

#--------------------------------------------------------------------------
def createFuncAnimation(zImag, zReal):

    #aktuallisieren der Artists für jeden Frame
    def update(frame):
        
        x = zReal[:frame+1]
        y = zImag[:frame+1]

        data = np.stack([x, y]).T #zusammenfügen der x und y Koordinaten und vertauschen der Zeilen und Spalten
        scat.set_offsets(data)
        return (scat)

    fig, ax = plt.subplots()
    
    #erstellen des initialen Plots
    scat = ax.scatter(zReal[0], zImag[0], s = 20,color='blue')  
    ax.set(xlim=[-0.3, 0.3], ylim=[-0.3, 0.3])
    ax.set_aspect('equal')

    #Animation
    #intervall in ms kann nicht kleiner werden als Wiederholrate von Monitor
    ani = animation.FuncAnimation(fig=fig, func=update, frames=numSamples, interval=100, repeat_delay = 2000) 

    plt.xlabel("Re", fontsize=14)  
    plt.ylabel("Im", fontsize=14)
    plt.tick_params(axis='both', labelsize=12)
    plt.show()
    
    return 0

#========================================Main========================================
os.chdir(r'Wav Dateien')

numSamples = 200         #Anzahl der Abtastwerte
numFreq = 3              #Anzahl der Berücksichtigen Frequenzen

out = False              #Ausgabe des Tons
showTransform = False    #Anzeigen des Frequenzspektrums 
showHamming = False      #Anzeigen des Hammingfensters
ani = False               #Animation
aniType = "Artist"         #Animations-Typ "Artist" oder "Func"   

filename = 'Sinus A-Moll.wav' #Audiodatei

#Einlesen der wav-Datei
data, fs = sf.read(filename, dtype='float32')
data = data[:,0] #Nur eine Seite der Stereodaten verwenden
N = len(data)
T = 1/fs

#Ausgeben der Wav-Datei
if out:
    sd.play(data, fs)
    status = sd.wait() 

#Fourieranalyse
window = np.hamming(len(data))
yf = np.fft.fft(data*window)
xf = np.fft.fftfreq(N, T)[:N//2]
yf = 2.0/N * np.abs(yf[0:N//2]) #Normalisierung

if showHamming:
    t = np.arange(0,len(data))
    fig, ax = plt.subplots()
    ax.plot(t,window)
    ax.grid()
    ax.set_xlabel('Samples n', fontsize=18)
    ax.set_ylabel('y[n]', fontsize=18)
    plt.tick_params(axis='both', labelsize=14)
    plt.show()

if showTransform:
    fig, ax = plt.subplots(constrained_layout=True)
    ax.plot(xf, yf)
    ax.grid()
    ax.set_xlabel("f in Hz", fontsize=18)  
    ax.set_ylabel("Ausprägung", fontsize=18) 
    plt.tick_params(axis='both', labelsize=14)
    plt.tight_layout()
    plt.show()

#sortieren des Arrays
nummerierung = np.arange(0, len(yf))
yf_num = np.column_stack((nummerierung,yf,xf)) #Nummerierung und Frequenzen Hinzufügen
yf_num = sorted(yf_num, key = lambda x:x[1], reverse = True)

createComplexPointers(yf_num, ani, aniType)