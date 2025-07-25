import requests
from bs4 import BeautifulSoup
import json

def debug_wbsc_page():
    """Debug function to analyze the WBSC page structure"""
    url = "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/schedule-and-results"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== PAGE TITLE ===")
        print(soup.title.text if soup.title else "No title found")
        
        print("\n=== LOOKING FOR GAME CONTAINERS ===")
        # Try different possible selectors
        selectors = [
            'div[class*="game"]',
            'div[class*="match"]',
            'div[class*="result"]',
            'div[class*="fixture"]',
            'tr[class*="game"]',
            'tr[class*="match"]',
            '.game-card',
            '.match-card',
            '.result-card'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                # Show first element structure
                if elements:
                    print(f"First element HTML: {str(elements[0])[:500]}...")
                    print()
        
        print("\n=== LOOKING FOR DATE SELECTORS ===")
        date_selectors = [
            'select[name*="date"]',
            'div[class*="date"]',
            'input[type="date"]',
            'a[href*="date"]',
            '.date-picker',
            '.calendar'
        ]
        
        for selector in date_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} date elements with selector: {selector}")
                if elements:
                    print(f"First element: {str(elements[0])[:300]}...")
                    print()
        
        print("\n=== CHECKING FOR TABLES ===")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables[:3]):  # Show first 3 tables
            print(f"\nTable {i+1} structure:")
            headers = table.find_all('th')
            if headers:
                print("Headers:", [th.text.strip() for th in headers])
            
            rows = table.find_all('tr')[:3]  # First 3 rows
            for j, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                print(f"Row {j+1}:", [cell.text.strip() for cell in cells][:5])
        
        print("\n=== CHECKING FOR SCRIPTS (AJAX/JSON DATA) ===")
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('game' in script.string.lower() or 'match' in script.string.lower() or 'result' in script.string.lower()):
                print("Found relevant script content (first 500 chars):")
                print(script.string[:500])
                print("---")
        
        # Save full HTML for manual inspection
        with open('page_debug.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("\n=== Full HTML saved to page_debug.html ===")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_wbsc_page()