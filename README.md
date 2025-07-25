# WBSC Tournament to Instagram Automation

🏆 **Automatische Extraktion von WBSC-Turnierdaten und Generierung von Instagram-Content**

## 🌟 Features

- ✅ **Cross-Domain Support**: Funktioniert mit `wbsc.org` und `wbsceurope.org`
- ✅ **Universell**: Softball & Baseball, alle Altersklassen
- ✅ **Rundenbasiert**: Unterscheidung zwischen Opening Round, Second Round, Playoffs
- ✅ **Instagram-Ready**: Fertige Captions und Canva-Templates
- ✅ **Robust**: Fehlerbehandlung und Rate Limiting

## 📁 Verzeichnisstruktur

```
WBSC2Instagram/
├── clean_scrapers/           # 🚀 Produktive Skripte
│   ├── wbsc_game_scraper.py         # Spieldaten extrahieren
│   ├── wbsc_standings_scraper.py    # Tabellenstände mit Runden
│   └── wbsc_instagram_generator.py  # Instagram-Content generieren
├── archive/                  # 📦 Archivierte Daten
│   ├── outputs/             # Vorherige Ausgabedateien
│   ├── debug/               # Debug-Dateien
│   └── temp/                # Temporäre Entwicklungsdateien
├── venv/                    # Python Virtual Environment
├── README.md               # Diese Datei
└── README_USAGE.md         # Detaillierte Anweisungen
```

## 🚀 Quick Start

### 1. Setup
```bash
# Repository klonen und Setup
cd WBSC2Instagram
source venv/bin/activate
```

### 2. Europäisches Turnier (wbsceurope.org)
```bash
URL="https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/"

# Spieldaten extrahieren
python clean_scrapers/wbsc_game_scraper.py "$URL"

# Komplette Turnierdaten mit Runden
python clean_scrapers/wbsc_standings_scraper.py "$URL" --mode complete

# Instagram-Content generieren
python clean_scrapers/wbsc_instagram_generator.py "$URL" --max-posts 8
```

### 3. Weltweites Turnier (wbsc.org)
```bash
URL="https://www.wbsc.org/en/events/2025-viii-u-12-baseball-world-cup/"

# Identische Verwendung für alle Domains
python clean_scrapers/wbsc_game_scraper.py "$URL"
python clean_scrapers/wbsc_standings_scraper.py "$URL" --mode complete  
python clean_scrapers/wbsc_instagram_generator.py "$URL" --max-posts 5
```

## 📊 Ausgabeformate

### Game Scraper
- **JSON**: Vollständige Spieldaten mit Innings, Statistiken, Officials
- **CSV**: Flache Struktur für Excel/Google Sheets

### Standings Scraper  
- **JSON**: Rundenbasierte Tabellenstände mit Metadaten und Turnier-Summary

### Instagram Generator
- **JSON**: Fertige Posts mit Captions, Template-Daten für Canva-Integration

## 🎯 Unterstützte Content-Typen

- **Enhanced Game Results**: Spielergebnisse mit Kontext und Statistiken
- **Round Standings**: Tabellenstände nach Runden differenziert
- **Tournament Progression**: Team-Fortschritt zwischen Runden  
- **Advanced Tournament Summary**: Turnier-Highlights und Insights

## 🌍 Unterstützte Turniere

### wbsceurope.org
- Europäische Meisterschaften (U-12, U-15, U-18, U-23, Senior)
- Softball & Baseball
- Qualifikationsturniere

### wbsc.org
- World Cups (U-12, U-15, U-18, U-23, Senior)
- Premier12, World Baseball Classic
- Olympische Qualifikation
- Continental Championships

## 💡 Anwendungsbeispiele

### Social Media Manager
```bash
# Tägliche Turnier-Updates
python clean_scrapers/wbsc_instagram_generator.py "$URL" --max-posts 3

# Vollständige Turnier-Zusammenfassung
python clean_scrapers/wbsc_standings_scraper.py "$URL" --mode complete
```

### Datenanalyse
```bash
# Alle Spieldaten für Statistiken
python clean_scrapers/wbsc_game_scraper.py "$URL" --output tournament_analysis

# CSV-Export für Excel-Analyse
# → Automatisch generierte .csv Datei verwenden
```

### Content Creation
```bash
# Instagram-Content mit Canva-Templates
python clean_scrapers/wbsc_instagram_generator.py "$URL" --output social_media_content

# → JSON enthält fertige Canva-Template-Daten
```

## 📋 Häufige Anwendungsfälle

1. **Live-Turnier-Updates**: Regelmäßige Extraktion während laufender Turniere
2. **Post-Tournament Analysis**: Vollständige Datenextraktion nach Turnierende  
3. **Social Media Automation**: Automatische Instagram-Post-Generierung
4. **Statistik-Reports**: CSV-Export für detaillierte Analysen
5. **Multi-Tournament Tracking**: Parallele Überwachung mehrerer Turniere

## 🔧 Erweiterte Optionen

Siehe `README_USAGE.md` für:
- Detaillierte Parameter-Beschreibungen
- Fehlerbehandlung und Troubleshooting
- Anpassung der Ausgabeformate
- Rate Limiting und Performance-Tuning

## 📈 Erfolgreich getestet mit

- **2025 U-18 Women's Softball European Championship** (63 Spiele, 2 Runden)
- **2025 VIII U-12 Baseball World Cup** (50 Spiele, 1 Runde)
- **Cross-Domain Kompatibilität** zwischen wbsc.org und wbsceurope.org

---

**Version**: 2.0 - Cross-Domain Support  
**Letztes Update**: 25. Juli 2025  
**Status**: ✅ Produktionsbereit für alle WBSC-Turniere