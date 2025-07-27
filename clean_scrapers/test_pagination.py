#!/usr/bin/env python3
"""
Schneller Test für die verbesserte WBSC Pagination
"""

import sys
import os
from wbsc_stats_scraper import WBSCStatscraper

def test_pagination():
    """Test die verbesserte Pagination"""
    url = "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/stats"
    
    print("🧪 Test: Verbesserte Pagination mit Duplicate-Detection")
    print("=" * 60)
    
    scraper = WBSCStatscraper(url, delay=0.5)  # Schnellerer Test
    
    print("📊 Scraping nur Batting-Statistiken...")
    
    # Scrape nur Batting mit den neuen Verbesserungen
    stats = scraper.scrape_all_stats(['batting'])
    
    batting_stats = stats.get('batting', [])
    
    print(f"\n✅ Ergebnisse:")
    print(f"🏆 Gesamte Spieler erfasst: {len(batting_stats)}")
    
    if batting_stats:
        print(f"👤 Erste Spielerin: {batting_stats[0].get('name')} ({batting_stats[0].get('team')})")
        print(f"👤 Letzte Spielerin: {batting_stats[-1].get('name')} ({batting_stats[-1].get('team')})")
        
        # Prüfe auf Duplikate
        names = [p.get('name', '') for p in batting_stats]
        unique_names = set(names)
        
        print(f"🔍 Duplikat-Check: {len(names)} Einträge, {len(unique_names)} einzigartige Namen")
        
        if len(names) != len(unique_names):
            print("⚠️  Duplikate gefunden!")
            duplicates = [name for name in unique_names if names.count(name) > 1]
            print(f"Duplikate: {duplicates[:5]}...")
        else:
            print("✅ Keine Duplikate gefunden!")
        
        # Zeige Teams
        teams = list(set(p.get('team', '') for p in batting_stats))
        print(f"🏅 Teams: {len(teams)} ({', '.join(sorted(teams))})")
        
    return len(batting_stats)

if __name__ == "__main__":
    try:
        total_players = test_pagination()
        print(f"\n🎉 Test erfolgreich abgeschlossen: {total_players} Spieler erfasst")
    except KeyboardInterrupt:
        print("\n⚠️  Test abgebrochen")
    except Exception as e:
        print(f"\n❌ Fehler: {e}") 