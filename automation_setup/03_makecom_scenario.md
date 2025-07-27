# Make.com Scenario für WBSC Story Generation

## Scenario Flow Overview
```
Webhook → JSON Parser → Iterator → Bannerbear → HTTP Download → Dropbox/Local
```

## Module Configuration

### 1. Webhook Trigger
```json
{
  "webhook_url": "https://hook.eu1.make.com/YOUR_URL",
  "method": "POST",
  "content_type": "application/json"
}
```

### 2. JSON Parser Module
```
Input: {{1.data}}
Parse: Root Level
Output: tournament, posts[]
```

### 3. Iterator Module
```
Array: {{2.posts}}
Iterations: Up to 100 posts per execution
```

### 4. Router für Post Types
```
Route 1: enhanced_game_result
  Filter: {{3.type}} = "enhanced_game_result"
  
Route 2: round_standings  
  Filter: {{3.type}} = "round_standings"
  
Route 3: tournament_progression
  Filter: {{3.type}} = "tournament_progression"
```

### 5. Bannerbear Modules (Per Route)

#### Route 1: Game Results
```json
{
  "template_id": "GAME_RESULT_TEMPLATE_ID",
  "modifications": [
    {
      "name": "winner_team",
      "text": "{{3.template_data.winner_team}}"
    },
    {
    "name": "winner_errors",
    "text": "{{3.template_data.winner_errors}}"
    },
    {
      "name": "winner_score", 
      "text": "{{3.template_data.winner_score}}"
    },
    {
    "name": "winner_hits", 
    "text": "{{3.template_data.winner_hits}}"
    },
    {
      "name": "loser_team",
      "text": "{{3.template_data.loser_team}}"
    },
    {
    "name": "loser_errors",
    "text": "{{3.template_data.loser_error}}"
    },
    {
      "name": "loser_score",
      "text": "{{3.template_data.loser_score}}"
    },
    {
    "name": "loser_hits",
    "text": "{{3.template_data.loser_hits}}"
    },
    {
      "name": "venue",
      "text": "{{3.template_data.venue}}"
    },
    {
      "name": "date",
      "text": "{{3.template_data.date}}"
    },
    {
      "name": "tournament_name",
      "text": "{{2.tournament.tournament_name}}"
    }
  ]
}
```

#### Route 2: Standings
```json
{
  "template_id": "STANDINGS_TEMPLATE_ID", 
  "modifications": [
    {
      "name": "round_name",
      "text": "{{3.template_data.round_name}}"
    },
    {
      "name": "tournament_name", 
      "text": "{{2.tournament.tournament_name}}"
    },
    {
      "name": "standings_text",
      "text": "{{3.template_data.standings_text}}"
    }
  ]
}
```

### 6. HTTP Download Module
```json
{
  "url": "{{5.image_url}}",
  "method": "GET",
  "filename": "{{2.tournament.tournament_slug}}_{{3.type}}_{{formatDate(now; 'YYYYMMDD_HHmmss')}}.png"
}
```

### 7. Dropbox/Local Save Module
```json
{
  "folder_path": "/WBSC_Stories/{{formatDate(now; 'YYYY-MM-DD')}}",
  "file_name": "{{6.filename}}",
  "file_data": "{{6.data}}"
}
```

## Error Handling
```
Error Handler auf jedem Modul:
- Action: "Resume"
- Retry: 3 attempts
- Delay: 30 seconds
```

## Testing Checklist
- [ ] Webhook empfängt JSON korrekt
- [ ] JSON Parser extrahiert Posts Array
- [ ] Iterator läuft durch alle Posts
- [ ] Router filtert Post Types korrekt
- [ ] Bannerbear generiert Images
- [ ] HTTP Download funktioniert
- [ ] Files werden lokal gespeichert
- [ ] Error Handling funktioniert

## Performance Optimization
```
Batch Size: 10 Posts per Run
Parallel Processing: Ja (Router)
Rate Limiting: 2 requests/second zu Bannerbear
Monitoring: Execution History aktivieren
```