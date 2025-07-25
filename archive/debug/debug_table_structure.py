import requests
from bs4 import BeautifulSoup

def debug_table_structure():
    """Debug the actual structure of the standings tables"""
    url = "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/standings"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find first standings table
        table = soup.find('table', class_='table table-hover standings-print')
        
        if table:
            print("=== FIRST TABLE STRUCTURE ===")
            
            # Print all rows
            rows = table.find_all('tr')
            
            for i, row in enumerate(rows):
                print(f"\nRow {i+1}:")
                cells = row.find_all(['td', 'th'])
                
                for j, cell in enumerate(cells):
                    print(f"  Cell {j+1}: '{cell.get_text(strip=True)}'")
                    print(f"    HTML: {str(cell)[:200]}...")
                
                if i >= 4:  # Just show first 5 rows
                    break
            
            print(f"\n=== LOOKING FOR GROUP INFO ===")
            # Find what's before the table
            current = table
            for i in range(10):
                current = current.find_previous_sibling()
                if not current:
                    break
                text = current.get_text(strip=True)
                if text:
                    print(f"Element {i+1} before table: '{text}'")
                    print(f"  Tag: {current.name}")
                    if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']:
                        print(f"  Classes: {current.get('class', [])}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_table_structure()