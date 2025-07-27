# Bannerbear Template Setup für WBSC Stories

## Account Setup
1. **URL:** https://www.bannerbear.com/
2. **Plan:** Growth Plan ($119/month) für 2,000 Images
3. **Test:** 30 kostenlose Images für Setup

## Template Design Strategy

### Template 1: Game Results (Minimal)
```
Format: 1080x1920 (Instagram Story)
Design Elements:
├── Header: Tournament Logo + Name
├── Main: Team Names + Scores (Large)
├── Sub: Venue + Date
└── Footer: Branded Hashtags

Variables:
- {{winner_team}}
- {{winner_score}} 
- {{loser_team}}
- {{loser_score}}
- {{venue}}
- {{date}}
- {{tournament_name}}
```

### Template 2: Game Results (Detailed)
```
Format: 1080x1920 (Instagram Story)
Design Elements:
├── Header: Tournament Logo + Name
├── Score Section: Teams + Final Score
├── Stats Section: Hits, Errors, Innings
├── Context: Venue, Date, Round
└── Footer: Branded Elements

Variables:
- {{winner_team}}
- {{winner_score}}
- {{loser_team}} 
- {{loser_score}}
- {{winner_hits}}
- {{loser_hits}}
- {{winner_errors}}
- {{loser_errors}}
- {{venue}}
- {{date}}
- {{round_info}}
```

### Template 3: Tournament Standings
```
Format: 1080x1920 (Instagram Story)
Design Elements:
├── Header: "STANDINGS" + Tournament Name
├── Round Info: "Opening Round" / "Second Round"
├── Group Table: Top 3-5 Teams
├── Stats: W-L, PCT, GB
└── Footer: Tournament Branding

Variables:
- {{round_name}}
- {{tournament_name}}
- {{group_name}}
- {{team_1_name}} + {{team_1_record}}
- {{team_2_name}} + {{team_2_record}}
- {{team_3_name}} + {{team_3_record}}
```

## Design Guidelines
### Colors (WBSC Brand)
- Primary: #1E3A8A (Navy Blue)
- Accent: #60A5FA (Light Blue)  
- Success: #059669 (Green)
- Alert: #DC2626 (Red)

### Typography
- Header: Bold, 48-56pt
- Scores: Extra Bold, 72-96pt
- Body: Regular, 24-32pt
- Footer: Light, 18-24pt

### Layout Grid
```
1080px width
├── Margins: 80px left/right
├── Header: 200px height
├── Content: 1200px height
├── Footer: 200px height
└── Safe Zone: 120px from edges
```

## Template Creation Steps
1. **Login** to Bannerbear Dashboard
2. **Create Template** → "Instagram Story"
3. **Add Elements:**
   - Background (Gradient/Solid)
   - Logo Upload (Your WBSC Logo)
   - Text Elements mit Variables
   - Decorative Elements
4. **Test Template** mit Sample Data
5. **API Key** generieren und notieren