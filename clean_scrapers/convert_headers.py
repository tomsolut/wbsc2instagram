#!/usr/bin/env python3
"""
Konvertiert bereits extrahierte Statistikdaten zu Frontend-Header-Format
"""

import pandas as pd
import json
import sys
import os
from datetime import datetime

def convert_to_frontend_headers():
    """Konvertiert die bereits extrahierten Daten zu Frontend-Headers"""
    
    # Mapping von alten zu neuen Header-Namen
    header_mapping = {
        'name': 'Player',
        'team': 'Team', 
        'games': 'G',
        'at_bats': 'AB',
        'runs': 'R',
        'hits': 'H',
        'doubles': '2B',
        'triples': '3B',
        'home_runs': 'HR',
        'rbi': 'RBI',
        'total_bases': 'TB',
        'batting_average': 'AVG',
        'slugging_percentage': 'SLG',
        'on_base_percentage': 'OBP',
        'ops': 'OPS',
        'walks': 'BB',
        'hit_by_pitch': 'HBP',
        'strikeouts': 'SO',
        'grounded_into_double_play': 'GDP',
        'sacrifice_flies': 'SF',
        'sacrifice_hits': 'SH',
        'stolen_bases': 'SB',
        'caught_stealing': 'CS'
    }
    
    # Pfad zur erfolgreich extrahierten Datei (automatische Erkennung)
    base_path = '../outputs'
    input_file = None
    
    # Suche nach der neuesten stats_batting Datei
    import glob
    pattern = f"{base_path}/*/stats_batting_*.csv"
    csv_files = glob.glob(pattern)
    
    if csv_files:
        # Nimm die neueste Datei
        input_file = max(csv_files, key=os.path.getmtime)
        print(f"📁 Gefundene Datei: {input_file}")
    else:
        # Fallback auf spezifische Datei
        input_file = '../outputs/2025-07-27_tournament/stats_batting_030626.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Eingabedatei nicht gefunden: {input_file}")
        return False
    
    try:
        # CSV laden
        df = pd.read_csv(input_file)
        print(f"📊 Lade {len(df)} Spieler-Records...")
        
        # Erstelle neue Datei mit Frontend-Headers
        df_converted = df.copy()
        
        # Header umbenennen
        columns_to_rename = {}
        for old_name, new_name in header_mapping.items():
            if old_name in df_converted.columns:
                columns_to_rename[old_name] = new_name
        
        df_converted = df_converted.rename(columns=columns_to_rename)
        
        # Timestamp für neue Datei
        timestamp = datetime.now().strftime('%H%M%S')
        # Verwende das gleiche Verzeichnis wie die Input-Datei
        output_dir = os.path.dirname(input_file)
        
        # Speichere als CSV mit Frontend-Headers
        csv_file = f"{output_dir}/stats_batting_frontend_{timestamp}.csv"
        df_converted.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Speichere auch als JSON
        json_file = f"{output_dir}/stats_frontend_{timestamp}.json"
        json_data = {
            'batting': df_converted.to_dict('records')
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Konvertierung erfolgreich!")
        print(f"📁 CSV: {csv_file}")
        print(f"📁 JSON: {json_file}")
        
        # Zeige Header-Vergleich
        print(f"\n🔄 Header-Konvertierung:")
        print(f"Alte Header: {', '.join(list(columns_to_rename.keys())[:10])}...")
        print(f"Neue Header: {', '.join(list(columns_to_rename.values())[:10])}...")
        
        # Zeige ersten Spieler als Beispiel
        if len(df_converted) > 0:
            first_player = df_converted.iloc[0]
            print(f"\n👤 Beispiel-Spieler:")
            print(f"Player: {first_player.get('Player', 'N/A')}")
            print(f"Team: {first_player.get('Team', 'N/A')}")
            print(f"G: {first_player.get('G', 'N/A')}, AB: {first_player.get('AB', 'N/A')}, AVG: {first_player.get('AVG', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Konvertierung: {e}")
        return False

if __name__ == "__main__":
    print("🔄 HEADER-KONVERTER: Normalisierte → Frontend Headers")
    print("=" * 60)
    
    success = convert_to_frontend_headers()
    
    if success:
        print("\n🎉 Konvertierung abgeschlossen!")
        print("Die Daten sind jetzt mit exakten Frontend-Headern verfügbar.")
    else:
        print("\n❌ Konvertierung fehlgeschlagen!")
        sys.exit(1) 