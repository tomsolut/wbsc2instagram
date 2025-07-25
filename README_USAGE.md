# WBSC Tournament to Instagram Automation - Usage Guide

## Übersicht

Diese Sammlung von Python-Skripten ermöglicht die automatische Extraktion von WBSC-Turnierdaten und deren Verarbeitung zu Instagram-Content. Alle Skripte sind generisch und können für verschiedene Turniere verwendet werden.

## Skripte

### 1. Game Results Scraper (`final_scrapers/wbsc_scraper_updated.py`)

Extrahiert alle Spieldaten aus einem WBSC-Turnier.

**Usage:**
```bash
python final_scrapers/wbsc_scraper_updated.py <TOURNAMENT_URL> [OPTIONS]
```

**Beispiel:**
```bash
python final_scrapers/wbsc_scraper_updated.py "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/"
```

**Optionen:**
- `--delay FLOAT`: Verzögerung zwischen Requests in Sekunden (Standard: 1.5)
- `--output STRING`: Ausgabedatei-Präfix (ohne Erweiterung)

**Output:**
- JSON-Datei mit allen Spieldaten
- CSV-Datei mit flachen Spieldaten

---

### 2. Round-Based Standings Scraper (`final_scrapers/round_based_standings_scraper.py`)

Extrahiert Tabellenstände mit Rundendifferenzierung (Opening Round, Second Round, etc.).

**Usage:**
```bash
python final_scrapers/round_based_standings_scraper.py <TOURNAMENT_URL> [OPTIONS]
```

**Beispiel:**
```bash
# Komplette Turnierdaten mit Runden
python final_scrapers/round_based_standings_scraper.py "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/" --mode complete

# Nur Tabellenstände
python final_scrapers/round_based_standings_scraper.py "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/" --mode standings
```

**Optionen:**
- `--delay FLOAT`: Verzögerung zwischen Requests in Sekunden (Standard: 1.5)
- `--output STRING`: Ausgabedatei-Präfix (ohne Erweiterung)
- `--mode {standings,complete}`: Modus - nur Tabellen oder komplette Turnierdaten (Standard: complete)

**Output:**
- JSON-Datei mit rundenbasierten Daten

---

### 3. Instagram Content Generator (`final_scrapers/final_round_based_instagram.py`)

Generiert Instagram-Content basierend auf Turnierdaten mit Rundendifferenzierung.

**Usage:**
```bash
python final_scrapers/final_round_based_instagram.py <TOURNAMENT_URL> [OPTIONS]
```

**Beispiel:**
```bash
python final_scrapers/final_round_based_instagram.py "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/" --max-posts 8
```

**Optionen:**
- `--delay FLOAT`: Verzögerung zwischen Requests in Sekunden (Standard: 1.5)
- `--output STRING`: Ausgabedatei-Präfix (ohne Erweiterung)
- `--max-posts INT`: Maximale Anzahl Posts (Standard: 10)

**Output:**
- JSON-Datei mit Instagram-Posts und Canva-Templates

---

## Workflow-Beispiel

### Vollständige Turnier-Verarbeitung:

#### Beispiel 1: Europäisches Turnier (wbsceurope.org)
```bash
# 1. Basis-URL des Turniers
TOURNAMENT_URL="https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/"

# 2. Spieldaten extrahieren
python final_scrapers/wbsc_scraper_updated.py "$TOURNAMENT_URL" --output tournament_games

# 3. Komplette Turnierdaten mit Runden extrahieren
python final_scrapers/round_based_standings_scraper.py "$TOURNAMENT_URL" --mode complete --output tournament_complete

# 4. Instagram-Content generieren
python final_scrapers/final_round_based_instagram.py "$TOURNAMENT_URL" --max-posts 8 --output tournament_instagram
```

#### Beispiel 2: Weltweites Turnier (wbsc.org)
```bash
# 1. Basis-URL des Turniers
TOURNAMENT_URL="https://www.wbsc.org/en/events/2025-viii-u-12-baseball-world-cup/"

# 2. Alle Skripte funktionieren identisch
python final_scrapers/wbsc_scraper_updated.py "$TOURNAMENT_URL"
python final_scrapers/round_based_standings_scraper.py "$TOURNAMENT_URL" --mode complete
python final_scrapers/final_round_based_instagram.py "$TOURNAMENT_URL" --max-posts 5
```

## URL-Format

Die Skripte funktionieren mit beiden WBSC-Domains und erwarten die Basis-URL des Turniers:

### ✅ Unterstützte Domains:
- **wbsceurope.org** - Europäische Turniere
- **wbsc.org** - Weltweite Turniere (World Cups, etc.)

### ✅ Gültige URL-Formate:
- `https://www.wbsceurope.org/en/events/tournament-name/`
- `https://www.wbsc.org/en/events/tournament-name/`
- `https://www.wbsceurope.org/en/events/tournament-name` (wird automatisch korrigiert)
- `https://www.wbsc.org/en/events/tournament-name` (wird automatisch korrigiert)

### ❌ Ungültige Formate:
- `https://www.wbsceurope.org/en/events/tournament-name/schedule-and-results` (zu spezifisch)

Die Skripte fügen automatisch die benötigten Pfade hinzu:
- Game Scraper: `/schedule-and-results`
- Standings Scraper: `/standings`

## Ausgabedateien

### Automatische Dateinamen

Wenn keine `--output` Option angegeben wird, generieren die Skripte automatisch Dateinamen:

```
wbsc_{tournament-name}_{timestamp}_{type}.{extension}
```

Beispiel:
```
wbsc_2025-u-18-womens-softball-european-championship_20250725_204154.json
```

### Dateiformate

**Game Results:**
- `.json`: Vollständige Spieldaten mit verschachtelten Strukturen
- `.csv`: Flache Datenstruktur für Spreadsheet-Programme

**Standings:**
- `.json`: Rundenbasierte Tabellenstände mit Metadaten

**Instagram Content:**
- `.json`: Posts mit Captions, Template-Daten und Canva-Integration

## Features

### ✅ Implementierte Features:
- **Generische URL-Parameter**: Funktioniert mit allen WBSC-Turnieren
- **Rundendifferenzierung**: Opening Round, Second Round, Playoffs, etc.
- **Rate Limiting**: Konfigurierbare Verzögerungen zwischen Requests
- **Fehlerbehandlung**: Robuste Skripte mit Logging
- **Flexible Ausgabe**: Anpassbare Dateinamen und Formate
- **Instagram-Integration**: Fertige Captions und Template-Daten
- **Canva-Ready**: Strukturierte Daten für Canva-Templates

### 🎯 Unterstützte Content-Typen:
- **Enhanced Game Results**: Spielergebnisse mit Kontext
- **Round Standings**: Tabellenstände nach Runden getrennt  
- **Tournament Progression**: Team-Fortschritt zwischen Runden
- **Advanced Tournament Summary**: Turnier-Highlights und Statistiken

## Fehlerbehandlung

Die Skripte enthalten umfassende Fehlerbehandlung:
- Automatische Wiederholung bei Netzwerkfehlern
- Graceful Degradation bei fehlenden Daten
- Ausführliche Logging-Informationen
- Validierung der URL-Parameter

## System-Anforderungen

- Python 3.7+
- Virtual Environment (empfohlen)
- Internetverbindung für WBSC-Website-Zugriff

### Installation:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Troubleshooting

### Häufige Probleme:

1. **"No games found"**: 
   - URL prüfen
   - Turnier-Status überprüfen
   - Delay erhöhen (`--delay 3.0`)

2. **"Connection timeout"**:
   - Internet-Verbindung prüfen
   - Delay erhöhen
   - VPN/Proxy-Einstellungen prüfen

3. **"No standings data"**:
   - Turnier könnte noch nicht begonnen haben
   - Standings-URL manuell prüfen
   - Mode auf 'complete' setzen

### Debugging:
```bash
# Verbose-Modus (mehr Logging-Informationen)
python -u final_scrapers/wbsc_scraper_updated.py "$URL" --delay 2.0
```

---

**Stand:** 25. Juli 2025  
**Version:** 2.0 - Generische URL-Parameter