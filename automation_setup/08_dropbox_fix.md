# Dropbox Data Parameter Fix

## Problem: "Missing value of required parameter 'data'"

### Ursache:
Das Dropbox-Modul erhält keine Bilddaten von Bannerbear. Die Datenübertragung ist falsch konfiguriert.

### Lösung:

#### 1. Dropbox Module konfigurieren

**AKTUELL (falsch):**
```
Data: {{6.filename}} oder {{6.data}}  // Falsche Modulreferenz
```

**RICHTIG (so einstellen):**
```
Folder: /[3] projects/wbsc2insta
File name: {{formatDate(now; "YYYYMMDD_HHmmss")}}_{{5.template}}.png
Data: {{5.image_url}}  // WICHTIG: Bannerbear image_url verwenden
Overwrite: false
```

#### 2. Bannerbear → Dropbox Datenfluss

**Bannerbear Modul Ausgabe:**
- `image_url` - URL zum generierten PNG
- `image_id` - Bannerbear Image ID
- `template` - Template Name

**Dropbox benötigt:**
- `data` Parameter muss die Bilddaten enthalten

#### 3. HTTP Download Modul hinzufügen (Empfohlen)

**Bessere Lösung:** HTTP Download zwischen Bannerbear und Dropbox:

```
Bannerbear → HTTP Download → Dropbox

HTTP Download Konfiguration:
URL: {{5.image_url}}
Method: GET
Output: Binary data

Dropbox Konfiguration:
Data: {{6.data}}  // Von HTTP Download
File name: story_{{formatDate(now; "YYYYMMDD_HHmmss")}}.png
```

#### 4. Alternative: Direkter Download

**Wenn kein HTTP Modul:** Dropbox direkt konfigurieren:
```
Data: {{5.image_url}}
```

#### 5. Dropbox Folder-Struktur

**Empfohlener Pfad:**
```
Folder: /[3] projects/wbsc2insta/{{formatDate(now; "YYYY-MM-DD")}}
File name: {{3.type}}_{{formatDate(now; "HHmmss")}}.png
```

**Beispiel-Ausgabe:**
```
/[3] projects/wbsc2insta/2025-07-25/enhanced_game_result_232744.png
/[3] projects/wbsc2insta/2025-07-25/round_standings_232745.png
```

### Testing:
Nach der Korrektur sollten PNG-Files erfolgreich in Dropbox gespeichert werden.