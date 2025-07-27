# Module Reference Fix

## Problem: "Referenced module 'Bannerbear - Create an Image' [5] is not accessible"

### Ursache:
Die Dropbox-Module verweisen auf falsche Modul-IDs. Die Bannerbear-Module haben andere IDs als erwartet.

### Lösung:

#### 1. Modulreferenzen prüfen
In Make.com → Scenario → **Modul-IDs identifizieren:**

**Aktuelle Struktur:**
```
[1] Webhook
[2] JSON Parser  
[3] Iterator
[4] Router
[5] Bannerbear (Route 1)
[6] Dropbox (Route 1)
[7] Bannerbear (Route 2)  
[8] Dropbox (Route 2)
```

#### 2. Dropbox Module korrigieren

**Route 1 (Dropbox nach erstem Bannerbear):**
```
Data: {{5.image_url}}  // Modul 5 = Erstes Bannerbear
File name: standings_{{formatDate(now; "HHmmss")}}.png
```

**Route 2 (Dropbox nach zweitem Bannerbear):**
```
Data: {{7.image_url}}  // Modul 7 = Zweites Bannerbear  
File name: game_result_{{formatDate(now; "HHmmss")}}.png
```

#### 3. Modulreferenzen visuell prüfen

**In Make.com Scenario:**
1. **Jedes Modul anklicken** → Zeigt die ID an
2. **Verbindungslinien folgen** → Von Bannerbear zu Dropbox
3. **Mapping korrigieren** → Richtige `{{X.image_url}}` verwenden

#### 4. Korrekte Datenflüsse

**Route 1:** Enhanced Game Results
```
Iterator [3] → Router [4] → Bannerbear [5] → Dropbox [6]
Dropbox Data: {{5.image_url}}
```

**Route 2:** Round Standings  
```
Iterator [3] → Router [4] → Bannerbear [7] → Dropbox [8]
Dropbox Data: {{7.image_url}}
```

#### 5. Alternative: Module neu verbinden

**Wenn Referenzen kaputt sind:**
1. **Dropbox-Module löschen**
2. **Neu hinzufügen** direkt nach Bannerbear
3. **Automatische Verbindung** erstellen lassen
4. **Data-Mapping** wird automatisch korrekt gesetzt

### Testing:
Nach der Korrektur sollten PNG-Files erfolgreich von Bannerbear zu Dropbox übertragen werden.