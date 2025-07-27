# WBSC Statistik-Scraper

Dieses Skript extrahiert Spielerstatistiken von WBSC-Turnierseiten in den Kategorien Batting, Pitching und Fielding.

## Funktionen

- ✅ Scraping von Batting-, Pitching- und Fielding-Statistiken
- ✅ Automatische Pagination-Unterstützung
- ✅ React-Daten-Extraktion und HTML-Fallback
- ✅ Ausgabe in JSON und CSV-Format
- ✅ Debug-Modus zur Seitenanalyse
- ✅ Robuste Fehlerbehandlung

## Installation

Stellen Sie sicher, dass alle erforderlichen Python-Bibliotheken installiert sind:

```bash
pip install requests beautifulsoup4 pandas
```

## Verwendung

### Grundlegende Nutzung

```bash
python wbsc_stats_scraper.py --url "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/stats"
```

### Mit benutzerdefinierten Optionen

```bash
python wbsc_stats_scraper.py \
  --url "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/stats" \
  --tournament-name "U18 Women's Softball European Championship 2025" \
  --output "outputs/my_tournament_stats" \
  --delay 2.0
```

### Debug-Modus

Verwenden Sie den Debug-Modus, um die Seitenstruktur zu analysieren, bevor Sie das vollständige Scraping starten:

```bash
python wbsc_stats_scraper.py \
  --url "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/stats" \
  --debug \
  --category batting
```

## Parameter

| Parameter | Beschreibung | Erforderlich |
|-----------|--------------|--------------|
| `--url` | URL der WBSC Statistik-Seite | ✅ Ja |
| `--output` | Ausgabeverzeichnis | ❌ Nein (automatisch generiert) |
| `--tournament-name` | Name des Turniers für Dateinamen | ❌ Nein |
| `--delay` | Verzögerung zwischen Anfragen in Sekunden | ❌ Nein (Standard: 1.0) |
| `--debug` | Debug-Modus aktivieren | ❌ Nein |
| `--category` | Kategorie für Debug-Modus | ❌ Nein (Standard: batting) |

## Ausgabeformate

Das Skript erstellt folgende Dateien:

### JSON-Datei
```
stats_HHMMSS.json
```
Enthält alle Statistiken in strukturiertem JSON-Format mit allen drei Kategorien.

### CSV-Dateien
```
stats_batting_HHMMSS.csv
stats_pitching_HHMMSS.csv  
stats_fielding_HHMMSS.csv
```
Separate CSV-Dateien für jede Statistik-Kategorie.

## Datenstruktur

### Batting-Statistiken
- `games` - Spiele
- `at_bats` - Schlagversuche
- `runs` - Runs
- `hits` - Hits
- `doubles` - Doubles
- `triples` - Triples
- `home_runs` - Home Runs
- `rbi` - RBI (Runs Batted In)
- `walks` - Walks
- `strikeouts` - Strikeouts
- `stolen_bases` - Gestohlene Bases
- `batting_average` - Schlagdurchschnitt
- `on_base_percentage` - On-Base-Percentage
- `slugging_percentage` - Slugging-Percentage

### Pitching-Statistiken
- `games` - Spiele
- `games_started` - Gestartete Spiele
- `complete_games` - Vollständige Spiele
- `wins` - Siege
- `losses` - Niederlagen
- `saves` - Saves
- `innings_pitched` - Geworfene Innings
- `hits_allowed` - Zugelassene Hits
- `runs_allowed` - Zugelassene Runs
- `earned_runs` - Earned Runs
- `walks_allowed` - Zugelassene Walks
- `strikeouts` - Strikeouts
- `era` - ERA (Earned Run Average)
- `whip` - WHIP (Walks + Hits per Inning Pitched)

### Fielding-Statistiken
- `games` - Spiele
- `putouts` - Putouts
- `assists` - Assists
- `errors` - Fehler
- `double_plays` - Double Plays
- `fielding_percentage` - Fielding-Percentage
- `range_factor` - Range Factor

## Fehlerbehandlung

Das Skript verfügt über mehrere Mechanismen zur Fehlerbehandlung:

1. **React-Daten-Extraktion**: Primäre Methode für moderne WBSC-Seiten
2. **HTML-Tabellen-Fallback**: Für Seiten ohne React-Daten
3. **Automatische Retry-Logik**: Bei temporären Netzwerkfehlern
4. **Flexible Feldmapping**: Für verschiedene Spaltenbezeichnungen

## Troubleshooting

### Keine Daten gefunden
1. Nutzen Sie den Debug-Modus: `--debug`
2. Überprüfen Sie die URL-Struktur
3. Prüfen Sie, ob die Seite Pagination verwendet

### Unterschiedliche Spaltenbezeichnungen
Das Skript erkennt automatisch verschiedene Bezeichnungen für Statistikfelder. Falls neue Bezeichnungen auftauchen, können diese in den `field_mappings` ergänzt werden.

### Netzwerk-Timeouts
Erhöhen Sie die Verzögerung: `--delay 3.0`

## Beispiel-Output

```
🏆 Starte Statistik-Scraping für: https://www.wbsceurope.org/.../stats
📊 Kategorien: Batting, Pitching, Fielding

INFO:Scraping batting statistics...
INFO:Processing batting page 1
INFO:Found 25 players on page 1
INFO:Processing batting page 2
INFO:Found 20 players on page 2
INFO:No more players found on page 3, stopping pagination
INFO:Total batting players scraped: 45

INFO:Scraping pitching statistics...
INFO:Total pitching players scraped: 15

INFO:Scraping fielding statistics...
INFO:Total fielding players scraped: 45

📊 Scraping Summary:
Total player records: 105
  - Batting: 45 players
  - Pitching: 15 players  
  - Fielding: 45 players
Files saved to: outputs/2025-07-26_u18_womens_softball_european_championship_2025
```

## Anpassungen

Für spezielle WBSC-Seiten können folgende Anpassungen nötig sein:

1. **URL-Parameter**: Ändern Sie die URL-Struktur in `_scrape_category_stats()`
2. **Feldmappings**: Erweitern Sie die `field_mappings` in `_process_html_player_data()`
3. **Tabellen-Erkennung**: Anpassen der `_is_stats_table()` Indikatoren 