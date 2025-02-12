import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from Audio import AudioOut, valsToMs
import math
import cmath

def processImage(img, val, draw = False):

    img = cv.cvtColor(img, cv.COLOR_BGR2RGB) #Anpassen für Matplotlib
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    
    _, thresh = cv.threshold(gray,120,255,cv.THRESH_BINARY_INV)

    # noise removal
    kernel = np.ones((3,3),np.uint8)
    opening = cv.morphologyEx(thresh,cv.MORPH_DILATE, kernel, iterations = 2)

    # sure background area
    sure_bg = cv.dilate(opening,kernel,iterations=3)

    # Finding sure foreground area
    dist_transform = cv.distanceTransform(opening,cv.DIST_L2,5)
    _, sure_fg = cv.threshold(dist_transform,0.1 * val *dist_transform.max(),255,0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv.subtract(sure_bg, sure_fg)
    _, markers = cv.connectedComponents(sure_fg)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0

    markers = np.int32(markers)
    markers_WsA = cv.watershed(img,markers)

    #Regionen im Bild markieren
    img[markers_WsA == -1] = [255,0,0]

    blank = np.zeros(img.shape, dtype='uint8')
    blank[markers_WsA == -1] = [255,255,255]
    blank_inv = 255 - blank

    #---------------------------plots---------------------------
    if draw == True:
        plt.figure(figsize=(4, 3),dpi=300)
        plt.subplot(231)
        plt.title("1. Bild in Graustufen", fontdict={'fontsize': 8, 'fontname': 'Times New Roman'})
        plt.imshow(gray, cmap = 'gray')
        plt.axis('off')
        plt.subplot(232)
        plt.title("2. Thresholding", fontdict={'fontsize': 8, 'fontname': 'Times New Roman'})
        plt.axis('off')
        plt.imshow(thresh, cmap='gray')
        plt.subplot(233)
        plt.title("3. Dilatation", fontdict={'fontsize': 8, 'fontname': 'Times New Roman'})
        plt.axis('off')
        plt.imshow(opening)
        plt.subplot(234)
        plt.title("4. Distanz-\ntransformation", fontdict={'fontsize': 8, 'fontname': 'Times New Roman'})
        plt.axis('off')
        plt.imshow(dist_transform)
        plt.subplot(235)
        plt.title("5. Thresholding und \n Hauptkomponentenanalyse", fontdict={'fontsize': 8, 'fontname': 'Times New Roman'})
        plt.axis('off')
        plt.imshow(markers)
        plt.subplot(236)
        plt.title("6. WsA\n ", fontdict={'fontsize': 8, 'fontname': 'Times New Roman'})
        plt.axis('off')
        plt.imshow(markers)
        plt.subplots_adjust(wspace=0.6, hspace=0.1)
        plt.show()
    #-----------------------------------------------------------

    #Extrahieren der einzelnen Conturen
    blank = cv.cvtColor(blank, cv.COLOR_RGB2GRAY)
    contours,_ = cv.findContours(blank, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)

    #Doppelte Konturen finden
    tolerance = 5     #toleranz in der ähnliche Konturen liegen müssen
    duplicate = []
    unique_contours = []
    
    for i, c1 in enumerate(contours):
        for j, c2 in enumerate(contours):
            if i < j:
                rect1 = cv.boundingRect(c1)     #besteht aus x,y Koordinate der oberen linken Ecke sowie Breite und Höhe
                rect2 = cv.boundingRect(c2)

                if abs(rect1[0] - rect2[0]) < tolerance and \
                   abs(rect1[1] - rect2[1]) < tolerance and \
                   abs(rect1[2] - rect2[2]) < tolerance and \
                   abs(rect1[3] - rect2[3]) < tolerance:      #Wenn sie ähnlich sind   
                                     
                    duplicate.append(i)

    for i, c in enumerate(contours):  #Alle conturen die nicht als doppelt gekennzeichnet wurden
        if i not in duplicate:
            unique_contours.append(c)

    return unique_contours

#===================================================================================================

def resize_with_aspect_ratio(img, target_width, target_height):

    original_width, original_height = img.size
    aspect_ratio = original_width / original_height

    # Zielgrößen berechnen, wobei das Seitenverhältnis beibehalten wird
    if target_width / target_height > aspect_ratio:
        # Zielhöhe limitierend
        new_height = target_height
        new_width = int(aspect_ratio * target_height)
    else:
        # Zielbreite limitierend
        new_width = target_width
        new_height = int(target_width / aspect_ratio)

    # Bild skalieren
    return img.resize((new_width, new_height))

#===================================================================================================

def contours2pic(contours, img, val = -1):
    blank = np.ones(img.shape, dtype='uint8')*255

    cont = np.arange(0,len(contours))

    for i in cont:
        if i == val:
            cv.drawContours(blank, contours, i, (255,0,0), 2) #einzeichnen der gefundenen Konturen in einem leeren Fenster
        else:
            cv.drawContours(blank, contours, i, (0,0,0), 1)
                                                    
    return blank

#===================================================================================================

def contour2melody(contour, chord, inst):
    global numArr
    x = contour[:,0,0]
    y = -contour[:,0,1]
    f_comp = x + 1j*y

    numArr = 50

    coeff = transformPicture(f_comp,1)  

    phase = np.empty((3,numArr))
    for i in range(numArr):
        f = abs(coeff[0,i])
        y = coeff[1,i]+coeff[1, 2*numArr-i]
        phase[0,i] = f                      #Frequenz
        phase[1,i] = abs(y)                 #Betrag
        p = cmath.phase(y)                  #Phase
        p = math.degrees(p) 

        if p < 0:
            p += 360                        #Anpassen, sodass die Phasenwinkel von 0 bis 360 Grad angegeben werden
        phase[2,i] = p   

    #sortiern des arrays der größe der Phase nach (absteigede Reihenfolge)
    indices = np.argsort(-phase[2,:])    #gibt Indizes des sortierten Arrays aus
    phase = phase[:, indices]        #ändert die Reihenfolge der Spalten anhand der Indizes

    #Rausfiltern der signifikanten Koeffizienten
    ind_play = np.where(phase[1] > phase[1,:].max()*0.05)[0] #np.mean(phase[1,:])
    play = phase[:,ind_play]   


    #Berechnen der Notenwerte
    noteVal = []
    limit = play[1,:].max()/3

    for i in play[1]:
        val = int(i / limit)
        if val == 0:
            val = 1
        elif val == 1:
            val = 2
        else:
            val = 4
        #val = 1
        noteVal.append(val)

    #Frequenzen in den hörbaren bereich verschieben und auf Töne mappen
    #Grundfrequenz ist c2 ~ 66Hz
    tones = []
    f_comp = 0
    last_note = ""
    for i in play[0]:
        f_comp = 0
        f = i * 66
        while f > 1046.5:
            f/=2
        for note, attribute in AudioOut.notes_freq.items():
            if abs(f-f_comp) < abs(f-attribute["frequency"]):
                tones.append(last_note)
                break
            f_comp = attribute["frequency"]
            last_note = note

    #ausgeben der Töne über die Klasse AudioOut
    duration = valsToMs(noteVal,bpm=120)
    audio = AudioOut(tones, inst, chord = chord, duration_ms=duration)
    audio.play()

    return

#===================================================================================================

def transformPicture(f_comp,n):
    global numArr
    coeff = np.empty(2*numArr+1, dtype=complex)
    freq = np.empty(2*numArr+1)

    time = np.linspace(0, 1, len(f_comp), endpoint = False) #erstellen des Zeitvektors
                                                            #dabei entspricht der letzte Punkt von f_comp dem ersten
                                                            #dieser darf nicht berücksichtigt werden daher endpoint = False
    deltaT = time[1]-time[0]

    #berechnen der komplexen Fourierreihe
    for i in range(-numArr, numArr+1):
        c_i = np.sum(f_comp * np.exp(-2 * np.pi * 1j * i * time)) * deltaT #numerisches integral
        coeff[i+numArr] = c_i
        freq[i+numArr] = i

    coeff_num = np.vstack((freq,coeff)) #Frequenzen und Koeffizienten zusammenfügen
    
    return coeff_num
