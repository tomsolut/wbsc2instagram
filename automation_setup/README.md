# WBSC Instagram Story Automation Setup

Automatisierte PNG-Generierung für Instagram Stories mit Make.com + Bannerbear.

## 🚀 Quick Start

### 1. Make.com Account Setup
```bash
# Folge den Anweisungen in:
cat 01_makecom_setup.md

# Webhook URL erhalten und testen:
python test_webhook.py https://hook.eu1.make.com/YOUR_WEBHOOK_URL
```

### 2. Bannerbear Templates
```bash
# Template-Design Guidelines:
cat 02_bannerbear_templates.md

# 3 Templates erstellen:
# - Game Results (Minimal)
# - Game Results (Detailed)  
# - Tournament Standings
```

### 3. Make.com Scenario
```bash
# Vollständige Workflow-Konfiguration:
cat 03_makecom_scenario.md

# Scenario in Make.com aufsetzen:
# Webhook → JSON Parser → Iterator → Router → Bannerbear → Download
```

### 4. Komplette Pipeline Testen
```bash
# Vollständige Integration testen:
python 04_integration_script.py \
  "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/" \
  "https://hook.eu1.make.com/YOUR_WEBHOOK_URL" \
  5
```

## 📂 File Structure

```
automation_setup/
├── 01_makecom_setup.md          # Make.com Account & Webhook Setup
├── 02_bannerbear_templates.md   # Template Design Specifications
├── 03_makecom_scenario.md       # Complete Workflow Configuration
├── 04_integration_script.py     # WBSC → Make.com Pipeline
├── test_webhook.py              # Webhook Testing Tool
└── README.md                    # This file
```

## 🔄 Workflow Overview

```
WBSC Tournament Data
         ↓
Python Scrapers (wbsc_instagram_generator.py)
         ↓
JSON Output (posts + metadata)
         ↓
Integration Script (04_integration_script.py)
         ↓
Make.com Webhook (receives JSON)
         ↓
JSON Parser (extracts posts array)
         ↓
Iterator (loops through posts)
         ↓
Router (routes by post type)
         ↓
Bannerbear (generates PNG images)
         ↓
HTTP Download (saves images locally)
         ↓
Instagram-Ready PNG Stories
```

## 🧪 Testing Strategy

### Phase 1: Individual Components
```bash
# Test webhook connectivity
python test_webhook.py https://hook.eu1.make.com/YOUR_URL

# Test scraper output format
cd ../clean_scrapers
python wbsc_instagram_generator.py "TOURNAMENT_URL" --max-posts 3
```

### Phase 2: Integration Testing
```bash
# Test complete pipeline with small dataset
python 04_integration_script.py "TOURNAMENT_URL" "WEBHOOK_URL" 3
```

### Phase 3: Production Validation
```bash
# Test with full tournament data
python 04_integration_script.py "TOURNAMENT_URL" "WEBHOOK_URL" 25
```

## 📊 Expected Output

### Scraper JSON Format:
```json
{
  "tournament": {
    "tournament_name": "2025 U-18 Women's Softball European Championship",
    "tournament_slug": "u18-womens-softball-european-2025",
    "year": "2025"
  },
  "posts": [
    {
      "type": "enhanced_game_result",
      "template_data": {
        "winner_team": "Spain",
        "winner_score": 7,
        "loser_team": "Germany", 
        "loser_score": 4,
        "venue": "Softball Stadium Prague",
        "date": "2025-07-25"
      },
      "caption": "🏆 GAME RESULT\n\nSpain defeats Germany 7-4..."
    }
  ]
}
```

### Bannerbear PNG Output:
- **Format:** 1080x1920 (Instagram Stories)
- **Naming:** `tournament-slug_post-type_timestamp.png`
- **Location:** Local downloads folder
- **Quality:** High-resolution, branded design

## 🔧 Configuration

### Environment Variables (Optional):
```bash
export MAKECOM_WEBHOOK_URL="https://hook.eu1.make.com/xxxxx"
export BANNERBEAR_API_KEY="bb_pr_xxxxxxxxxxxxx"
export DOWNLOAD_FOLDER="/Users/thomas/WBSC_Stories"
```

### Make.com Settings:
- **Error Handling:** Resume (3 retries, 30s delay)
- **Rate Limiting:** 2 requests/second to Bannerbear
- **Batch Size:** 10 posts per execution
- **Monitoring:** Execution history enabled

## 🚨 Troubleshooting

### Common Issues:

**Webhook 404/403:**
```bash
# Check webhook URL format
echo "Should be: https://hook.eu1.make.com/xxxxx"
# Verify Make.com scenario is active
```

**Bannerbear Template Errors:**
```bash
# Verify template variables match JSON structure
# Check API key permissions
# Validate image generation quota
```

**Download Failures:**
```bash
# Check local folder permissions
# Verify internet connectivity
# Monitor Make.com execution logs
```

## 📈 Performance Metrics

- **Scraping Speed:** ~30 games/minute
- **Image Generation:** ~10 images/minute
- **Total Pipeline:** ~5 minutes for full tournament
- **Cost:** ~€0.10 per story (Bannerbear)

## 🎯 Next Steps

1. **Setup Phase:** Complete all 4 configuration documents
2. **Testing Phase:** Validate with sample tournament data  
3. **Production Phase:** Deploy for live tournaments
4. **Optimization Phase:** Batch processing, error handling
5. **Scaling Phase:** Multiple tournaments, template variations