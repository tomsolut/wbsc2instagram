# Bannerbear Color Error Fix

## Problem: "[400] 0 is not a valid color for color" / "[400] 8 is not a valid color for color"

### Ursache:
Bannerbear erhält numerische Werte (0, 8) als Color-Parameter, aber erwartet Hex-Farben oder Farbnamen.

### Lösung:

#### 1. Template-Elemente prüfen
In Bannerbear Dashboard → Template bearbeiten:
- Elemente mit **Color-Properties** identifizieren
- Diese werden fälschlicherweise mit Zahlenwerten befüllt

#### 2. Make.com Modifications korrigieren

**PROBLEM:** Aktuell werden Score-Werte als Color-Parameter gesendet:
```
Name: some_color_element
Text: {{3.template_data.winner_score}}  // Das sind Zahlen wie 0, 8
```

**LÖSUNG:** Color-Parameter entfernen oder korrekt setzen:

**Option A - Color-Parameter entfernen:**
```
Löschen Sie alle Modifications mit Color-Properties:
- Keine "color" Felder in den Modifications
- Nur Text-Felder verwenden
```

**Option B - Korrekte Farben setzen:**
```
Name: team_color
Text: #1E3A8A  // WBSC Navy Blue

Name: score_color  
Text: #DC2626   // Red für Verlierer

Name: winner_color
Text: #059669   // Green für Gewinner
```

#### 3. Bannerbear Template bereinigen

In Bannerbear Template Designer:
1. **Alle Color-Elemente identifizieren**
2. **Feste Farben setzen** (nicht variabel)
3. **Nur Text-Variablen verwenden** für:
   - winner_team
   - winner_score  
   - loser_team
   - loser_score
   - venue
   - date
   - tournament_name

#### 4. Make.com Modifications bereinigen

Entfernen Sie alle Color-Modifications, behalten Sie nur:
```
[Add Item] → Name: winner_team, Text: {{3.template_data.winner_team}}
[Add Item] → Name: winner_score, Text: {{3.template_data.winner_score}}
[Add Item] → Name: loser_team, Text: {{3.template_data.loser_team}}
[Add Item] → Name: loser_score, Text: {{3.template_data.loser_score}}
[Add Item] → Name: venue, Text: {{3.template_data.venue}}
[Add Item] → Name: date, Text: {{3.template_data.date}}
[Add Item] → Name: tournament_name, Text: {{2.tournament.tournament_name}}
```

### Nach der Korrektur:
Die Bannerbear-Module sollten erfolgreich PNG-Images generieren ohne Color-Errors.