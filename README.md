# Sonifikation-von-Bildern
## Erklärung zu den Inhalten
### Ordner

**Beispielbilder**
Der Ordner beinhaltet zwei Bilder, anhand denen die Bildverarbeitung durchgeführt werden kann.
Wenn ein Bild keine guten Ergebnisse liefert, kann es hilfreich sein die Helligkeit und den Kontast anzupassen.

**Samples**
In diesem Ordner befinden sich Klaviersamples für alle Töne der C-Dur Tonleiter von C2 bis C6 in Form von WAVE-Dateien.

**Wav Daeteien**
In diesem Ordner befinden sich beispielhafte WAVE-Dateien zur Erstellung einer Figur.

### Phyton-Skripte

**Figur_aus_WAVE**
Mit Hilfe des Skriptes können Figuren aus WAVE-Dateien erstellt werden. Die Dateien dürfen nur Töne zwischen C3 unc C5 enthalten.
Über die Parameter "ani" und "aniType" kann eingestellt werden ob eine Animation erstellt werden soll und wenn ja welche.

**grafische_Oberfläche**
In diesem Skript sind Controller und View der GUI implementiert. Ein Ausführen der Datei startet die GUI.
In der GUI habe ich noch einen weiteren Knopf "Verarbeitungsschritte" hinzugefügt. Über diesen kann ausgewählt werden ob die einzelnen Bildverarbeitungsschritte in einem seperaten Plot angezeigt werden sollen oder nicht.

**Bildverarbeitung**
Hier ist das Model der GUI implementiert. In diesem Skript sind alle Funktionen zur Bildverarbeitung und Erstellung der Tonfolgen.

**Audio**
Hier ist die Klasse "AudioOut" zur Ausgabe der Tonfolgen implementiert. Zur Ausgabe werden die Dateien aus dem Ordner "Samples" benötigt.
