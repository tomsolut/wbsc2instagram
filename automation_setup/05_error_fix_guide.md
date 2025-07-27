# Make.com Error Fix Guide

## Problem: "Referenced module 'Flow Control - Resume' is not accessible"

### Ursache:
Die Error Handler Module sind nicht korrekt mit den Hauptmodulen verbunden.

### Lösung:

#### 1. Error Handler entfernen
```
Für jedes betroffene Modul:
1. Rechtsklick auf das Modul
2. "Error handler" → "Remove error handler"
3. Bestätigen
```

#### 2. Neue Error Handler hinzufügen
```
Für jedes Modul einzeln:
1. Rechtsklick auf das Modul
2. "Add error handler"
3. Wählen: "Flow Control" → "Resume"
4. Konfiguration:
   - Action: "Resume"
   - Number of retries: 3
   - Interval between retries: 30 seconds
```

#### 3. Scenario Struktur ohne Error Handler (Einfacher Start)
```
Webhook → JSON Parser → Iterator → Router → Bannerbear → HTTP Download → Dropbox
```

### Alternative: Scenario ohne Error Handler
Für erste Tests können Sie die Error Handler komplett weglassen:

1. **Alle Error Handler entfernen**
2. **Scenario testen** mit einfacher Struktur
3. **Error Handler später hinzufügen** wenn alles funktioniert

### Test nach Fix:
```bash
python test_webhook.py https://hook.eu2.make.com/a03kjvt9l9ev3ihlb31arusg51tmqkq3
```

### Scenario Status prüfen:
- Make.com Dashboard → Ihr Scenario
- Status sollte "ON" bleiben
- Keine roten Warnungen bei Modulen
- Execution History sollte grüne Ausführungen zeigen

### Vereinfachte Scenario-Struktur für Start:
```
1. Webhook (Custom webhook)
2. JSON Parser (Parse JSON)
3. Iterator (Array iterator) 
4. Bannerbear (Create image)
5. HTTP (Download file)
6. Dropbox (Upload file)
```

**Erst wenn diese Grundstruktur funktioniert, Router und Error Handler hinzufügen.**