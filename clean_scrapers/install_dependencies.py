#!/usr/bin/env python3
"""
Installationsskript für WBSC Stats Scraper Abhängigkeiten
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} erfolgreich installiert")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Fehler beim Installieren von {package}")
        return False

def check_chromedriver():
    """Check if ChromeDriver is available"""
    try:
        import shutil
        return shutil.which("chromedriver") is not None
    except:
        return False

def main():
    print("🔧 Installation der WBSC Stats Scraper Abhängigkeiten")
    print("=" * 60)
    
    # Required packages
    required_packages = [
        "requests",
        "beautifulsoup4", 
        "pandas",
        "lxml"
    ]
    
    # Optional packages for JavaScript rendering
    optional_packages = [
        ("selenium", "Für JavaScript-Rendering (empfohlen)"),
        ("requests-html", "Alternative für JavaScript-Rendering"),
        ("webdriver-manager", "Automatisches ChromeDriver Management")
    ]
    
    print("📦 Installiere erforderliche Pakete...")
    success_count = 0
    for package in required_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n✅ {success_count}/{len(required_packages)} erforderliche Pakete installiert")
    
    print("\n🌐 Installiere optionale Pakete für JavaScript-Rendering...")
    response = input("Möchten Sie die JavaScript-Rendering-Pakete installieren? (j/n): ").lower().strip()
    
    if response in ['j', 'ja', 'y', 'yes']:
        optional_success = 0
        for package, description in optional_packages:
            print(f"\n📥 Installiere {package} - {description}")
            if install_package(package):
                optional_success += 1
        
        print(f"\n✅ {optional_success}/{len(optional_packages)} optionale Pakete installiert")
        
        # Check ChromeDriver
        if check_chromedriver():
            print("✅ ChromeDriver ist verfügbar")
        else:
            print("⚠️  ChromeDriver nicht gefunden")
            print("   Sie können es installieren mit:")
            print("   - brew install chromedriver  (macOS)")
            print("   - oder webdriver-manager wird es automatisch herunterladen")
    
    print("\n🎉 Installation abgeschlossen!")
    print("\nSie können jetzt das Statistik-Scraping verwenden:")
    print("python wbsc_stats_scraper.py --url 'https://...' --debug")

if __name__ == "__main__":
    main() 