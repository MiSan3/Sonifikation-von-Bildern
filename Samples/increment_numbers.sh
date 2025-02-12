#!/bin/bash

# Verzeichnis festlegen (Standard: aktuelles Verzeichnis)
DIR="${1:-.}"

# Überprüfen, ob das Verzeichnis existiert
if [ ! -d "$DIR" ]; then
    echo "Das Verzeichnis '$DIR' existiert nicht."
    exit 1
fi

# Dateien sortieren, basierend auf der höchsten Zahl im Namen (absteigend)
FILES=$(ls "$DIR" | grep -E '[0-9]+' | sort -t '.' -k1,1r -n)

# Dateien umbenennen
for FILE in $FILES; do
    # Pfad zur Datei
    FULL_PATH="$DIR/$FILE"

    # Überprüfen, ob es sich um eine Datei handelt
    if [ -f "$FULL_PATH" ]; then
        # Originaler Dateiname ohne Pfad
        BASENAME=$(basename "$FULL_PATH")

        # Extrahiere Namen (ohne Erweiterung) und Erweiterung
        NAME="${BASENAME%.*}"  # Dateiname ohne Extension
        EXT="${BASENAME##*.}"  # Extension der Datei

        # Suche und erhöhe die erste Zahl im Namen
        if [[ "$NAME" =~ ([0-9]+) ]]; then
            NUMBER="${BASH_REMATCH[1]}" # Gefundene Zahl
            NEWNUMBER=$((NUMBER + 1))  # Zahl um eins erhöhen

            # Ersetze die alte Zahl durch die neue im Namen
            NEWNAME=$(echo "$NAME" | sed -E "s/$NUMBER/$NEWNUMBER/")

            # Kombiniere den neuen Namen mit der Erweiterung
            NEWFILE="${NEWNAME}.${EXT}"

            # Überprüfen, ob der neue Name sich unterscheidet und umbenennen
            if [ "$BASENAME" != "$NEWFILE" ]; then
                mv "$FULL_PATH" "$DIR/$NEWFILE"
                echo "Umbenannt: $BASENAME -> $NEWFILE"
            fi
        fi
    fi
done
