import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
from Bildverarbeitung import processImage, contours2pic, contour2melody, resize_with_aspect_ratio

#Globale Variable zum Speichern des Originalbilds
original_image = None
processed_image = None
contours = None
steps = False


# Funktion zum Einlesen eines Bildes
def load_image():
    global original_image, processed_image, contours
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp")])
    if file_path:
        original_image = Image.open(file_path)
        processed_image = None  # Bearbeitetes Bild leeren
        processed_image_label.config(image=None)  # Bildanzeige für bearbeitetes Bild leeren
        processed_image_label.image = None
        contours = None
        display_image()

# Funktion zum Anzeigen eines Bildes im Tkinter-Fenster
def display_image():
    global original_image, processed_image

    #Originalbild anzeigen
    orig_img = resize_with_aspect_ratio(original_image, 400, 400)
    tk_orig_image = ImageTk.PhotoImage(orig_img)
    original_image_label.config(image=tk_orig_image)
    original_image_label.image = tk_orig_image

    #Verarbeitetes Bild anzeigen
    if processed_image:
        proc_img = resize_with_aspect_ratio(processed_image, 400, 400)
        tk_proc_image = ImageTk.PhotoImage(proc_img)
        processed_image_label.config(image=tk_proc_image)
        processed_image_label.image = tk_proc_image

#Wiedergeben der Kontur
def play_contour():
    global contours
    if contours:
        cont = dropdown_var.get()  # Ausgewählte Option aus dem Dropdown
        chord = dropdown_varchord.get()
        if chord == "Chord":
            chord = True
        else:
            chord = False
        inst = dropdown_inst.get()
        contour2melody(contours[int(cont)], chord, inst)

#Callback neuer Wert im Dropdownmenü ausgewählt
def selected_changed(event):
    global processed_image
    val = dropdown.get()

    img_cv = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)

    img_cv = contours2pic(contours, img_cv, int(val))

    # Konvertiere OpenCV-Bild zurück in PIL-Bild       
    processed_image = Image.fromarray(img_cv)

    display_image()


# Funktion zur Bildverarbeitung
def process_image():
    global original_image, processed_image, contours
    if original_image:
        val = slider.get()  # Wert des Schiebereglers

        # Konvertiere PIL-Bild in OpenCV-Bild
        img_cv = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)

        contours = processImage(img_cv, val, draw=steps)

        # Dropdown-Werte aktualisieren
        new_options = np.arange(0,len(contours)).tolist()
        dropdown['values'] = new_options
        dropdown_var.set(new_options[0])

        img_cv = contours2pic(contours, img_cv)

        # Konvertiere OpenCV-Bild zurück in PIL-Bild       
        processed_image = Image.fromarray(img_cv)

        display_image()

def show_steps():
    global steps
    steps = not steps
    if steps:
        show_button.config(text="Anzeigen")
    else:
        show_button.config(text="Nicht Anzeigen")
#======================================================================

#Erstelle die Hauptoberfläche
root = tk.Tk()
root.title("Sonifikation von Bildern")

#=============================Bildanzeige=============================#
image_frame = tk.Frame(root)
image_frame.pack(pady=10, side=tk.TOP)

original_image_label = tk.Label(image_frame)
original_image_label.pack(side=tk.LEFT, padx=10)

processed_image_label = tk.Label(image_frame)
processed_image_label.pack(side=tk.RIGHT, padx=10)

#=============================Steuerelemente=============================#
controls_frame = tk.Frame(root)
controls_frame.pack(pady=20, side=tk.TOP)

#=============================Links=============================#
# Frame links unten
left_frame = tk.Frame(controls_frame)
left_frame.pack(side=tk.LEFT, padx=10)

#Knopf zum Laden eines Bilds
load_button = tk.Button(left_frame, text="Bild laden", command=load_image)
load_button.pack(pady=5)

# Label als Titel für das Dropdown-Menü
label_show = tk.Label(left_frame, text="Verarbeitungsschritte:")
label_show.pack()

#Auswahl des Instruments
show_button = tk.Button(left_frame, text="Nicht Anzeigen", command=show_steps)
show_button.pack(pady=5)

#=============================Mitte=============================#
#Frames für Bildverarbeitung mitte
middle_frame = tk.Frame(controls_frame)
middle_frame.pack(side=tk.LEFT, padx=20)

#Schieberegler
slider = tk.Scale(middle_frame, from_=0, to=10, orient=tk.HORIZONTAL, label="Intensität")
slider.pack(pady=10)

#Knopf für Verarbeiten
process_button = tk.Button(middle_frame, text="Verarbeiten", command=process_image)
process_button.pack(pady=5)

#=============================Rechts=============================#
# Frame für Ausgabe (rechts)
right_frame = tk.Frame(controls_frame)
right_frame.pack(side=tk.RIGHT, padx=20)

#Auswahl der Kontur per Dropdownmenü
options = ["-"]
dropdown_var = tk.StringVar(value=options[0])
dropdown = ttk.Combobox(right_frame, textvariable=dropdown_var, values=options, state="readonly")
dropdown.pack(pady=10)
dropdown.bind("<<ComboboxSelected>>", selected_changed) #callback wenn was neues ausgewählt wird

#Auswahl der Ausgabeart
options_chord = ["Chord", "Melody"]
dropdown_varchord = tk.StringVar(value=options_chord[0])
dropdown_chord = ttk.Combobox(right_frame, textvariable=dropdown_varchord, values=options_chord, state="readonly")
dropdown_chord.pack(pady=10)

#Auswahl des Instruments
options_inst = ["Piano", "Sine"]
dropdown_varinst = tk.StringVar(value=options_inst[0])
dropdown_inst = ttk.Combobox(right_frame, textvariable=dropdown_varinst, values=options_inst, state="readonly")
dropdown_inst.pack(pady=10)

#Knopf zum Ausgeben
process_button = tk.Button(right_frame, text="Ausgeben", command=play_contour)
process_button.pack(pady=5)

# Starte die Tkinter-Oberfläche
root.mainloop()