import requests
from bs4 import BeautifulSoup
import json
import html

def extract_react_data():
    """Extract the React data from the WBSC page"""
    url = "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/schedule-and-results"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the div with data-page attribute
        data_div = soup.find('div', {'data-page': True})
        
        if data_div:
            # Get the JSON data
            data_page = data_div.get('data-page')
            
            # Decode HTML entities
            decoded_data = html.unescape(data_page)
            
            # Parse JSON
            page_data = json.loads(decoded_data)
            
            print("=== EXTRACTED PAGE DATA ===")
            print(json.dumps(page_data, indent=2)[:2000] + "...")
            
            # Save to file for inspection
            with open('extracted_data.json', 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
            
            print("\n=== LOOKING FOR GAMES DATA ===")
            props = page_data.get('props', {})
            
            # Check for various possible game data locations
            possible_keys = ['games', 'matches', 'schedule', 'results', 'fixtures', 'tournament']
            for key in possible_keys:
                if key in props:
                    print(f"Found {key}: {type(props[key])}")
                    if isinstance(props[key], list):
                        print(f"  Contains {len(props[key])} items")
                        if props[key]:
                            print(f"  First item: {list(props[key][0].keys()) if isinstance(props[key][0], dict) else props[key][0]}")
            
            # Look for any data that might contain tournament info
            print("\n=== ALL PROPS KEYS ===")
            for key in props.keys():
                print(f"{key}: {type(props[key])}")
            
            return page_data
        else:
            print("No data-page div found")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    extract_react_data()