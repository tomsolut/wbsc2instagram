# Make.com Setup für WBSC Instagram Story Automation

## Account Registration
1. **URL:** https://www.make.com/en/register
2. **Plan:** Kostenlos für erste 1,000 Operations
3. **Upgrade:** Pro Plan ($16/month) für 10,000 Operations

## Webhook Setup
### Webhook URL erstellen:
1. Neues Scenario erstellen
2. Trigger: "Webhooks" → "Custom webhook"  
3. Webhook URL kopieren (Format: `https://hook.eu1.make.com/xxx`)

### Test Webhook:
```bash
curl -X POST https://hook.eu2.make.com/na1jxsvs5ty6s6cg7h48gtn8ud5pcser \
  -H "Content-Type: application/json" \
  -d '{
    "tournament": {
      "tournament_name": "Test Tournament",
      "year": "2025"
    },
    "posts": [
      {
        "type": "enhanced_game_result",
        "template_data": {
          "winner_team": "Spain",
          "winner_score": 5,
          "loser_team": "Germany", 
          "loser_score": 2,
          "venue": "Test Stadium",
          "date": "2025-07-25"
        }
      }
    ]
  }'
```

## Integration Module hinzufügen
1. **Bannerbear Module** hinzufügen
2. **HTTP Module** für Downloads
3. **JSON Module** für Datenverarbeitung

## Wichtige Settings
- **Error Handling:** "Resume" für robuste Workflows
- **Scheduling:** "Immediately" für Live-Updates  
- **Data Storage:** Aktivieren für Retry-Logic