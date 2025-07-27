  # Bannerbear Configuration Fix

## Problem: "Array of objects expected in parameter 'modifications'"

### Ursache:
Die Bannerbear-Module sind falsch konfiguriert. Die `modifications` müssen als **Array** eingegeben werden, nicht als JSON-Text.

### Lösung:

#### 1. Bannerbear Module öffnen
```
In Make.com → Ihr Scenario → Bannerbear Module anklicken
```

#### 2. Modifications korrekt konfigurieren

**FALSCH (aktuell):**
```json
{
  "template_id": "...",
  "modifications": [...]
}
```

**RICHTIG (so eingeben):**
```
Modifications: [Add Item] klicken für jedes Feld:

Item 1:
- Name: winner_team
- Text: {{3.template_data.winner_team}}

Item 2:
- Name: winner_score
- Text: {{3.template_data.winner_score}}

Item 3:
- Name: loser_team
- Text: {{3.template_data.loser_team}}

Item 4:
- Name: loser_score
- Text: {{3.template_data.loser_score}}

Item 5:
- Name: venue
- Text: {{3.template_data.venue}}

Item 6:
- Name: date
- Text: {{3.template_data.date}}

Item 7:
- Name: tournament_name
- Text: {{2.tournament.tournament_name}}
```

#### 3. Für Game Results Template:
```
Template UID: [Ihre Game Results Template ID]

Modifications:
[Add Item] → Name: winner_team, Text: {{3.template_data.winner_team}}
[Add Item] → Name: winner_score, Text: {{3.template_data.winner_score}}
[Add Item] → Name: loser_team, Text: {{3.template_data.loser_team}}
[Add Item] → Name: loser_score, Text: {{3.template_data.loser_score}}
[Add Item] → Name: venue, Text: {{3.template_data.venue}}
[Add Item] → Name: date, Text: {{3.template_data.date}}
[Add Item] → Name: tournament_name, Text: {{2.tournament.tournament_name}}
```

#### 4. Für Standings Template:
```
Template UID: [Ihre Standings Template ID]

Modifications:
[Add Item] → Name: round_name, Text: {{3.template_data.round_name}}
[Add Item] → Name: tournament_name, Text: {{2.tournament.tournament_name}}
[Add Item] → Name: standings_text, Text: {{3.template_data.standings_text}}
```

### Wichtig:
- **NICHT** als JSON eingeben
- **JA** über [Add Item] Button jedes Feld einzeln hinzufügen
- **Kein** `modifications` JSON-Block verwenden

### Nach der Korrektur:
1. Scenario speichern
2. Pipeline erneut testen:
```bash
python 04_integration_script.py "TOURNAMENT_URL" "WEBHOOK_URL" 3
```