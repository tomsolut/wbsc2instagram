import requests
from bs4 import BeautifulSoup

def debug_pagination_buttons():
    """Debug function to find pagination buttons and round names"""
    url = "https://www.wbsceurope.org/en/events/2025-u-18-womens-softball-european-championship/standings"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("=== LOOKING FOR PAGINATION ELEMENTS ===")
        
        # Look for different pagination patterns
        pagination_selectors = [
            '.pagination',
            '.nav-tabs',
            '.tab-content',
            '.nav-pills',
            'ul.nav',
            '.btn-group',
            '[role="tablist"]',
            'button[data-toggle]',
            'a[data-toggle]',
            '.nav a',
            '.tabs',
            '.rounds'
        ]
        
        for selector in pagination_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\nFound {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements[:2]):
                    print(f"Element {i+1}:")
                    print(f"  Text: '{elem.get_text(strip=True)}'")
                    print(f"  HTML: {str(elem)[:300]}...")
                    
                    # Look for child elements (buttons, links)
                    children = elem.find_all(['a', 'button', 'li'])
                    if children:
                        print(f"  Children:")
                        for j, child in enumerate(children[:5]):
                            print(f"    {j+1}: '{child.get_text(strip=True)}' - {child.name}")
                            if child.get('href'):
                                print(f"       href: {child.get('href')}")
                            if child.get('data-toggle'):
                                print(f"       data-toggle: {child.get('data-toggle')}")
        
        print("\n=== LOOKING FOR ROUND/TAB INDICATORS ===")
        
        # Look for elements containing "round", "opening", "second", etc.
        round_keywords = ['round', 'opening', 'second', 'preliminary', 'final', 'bracket']
        
        for keyword in round_keywords:
            elements = soup.find_all(text=lambda text: text and keyword.lower() in text.lower())
            if elements:
                print(f"\nFound '{keyword}' in text:")
                for elem in elements[:5]:
                    parent = elem.parent if elem.parent else None
                    if parent:
                        print(f"  Text: '{elem.strip()}'")
                        print(f"  Parent: {parent.name} - {parent.get('class', [])}")
                        print(f"  Parent text: '{parent.get_text(strip=True)[:100]}...'")
        
        print("\n=== LOOKING FOR BUTTONS AND LINKS ===")
        
        # Find all buttons and links that might control pagination
        buttons = soup.find_all(['button', 'a'], text=lambda text: text and any(
            keyword in text.lower() for keyword in ['round', 'opening', 'second', 'preliminary', 'final']
        ))
        
        for button in buttons:
            print(f"\nButton/Link found:")
            print(f"  Text: '{button.get_text(strip=True)}'")
            print(f"  Tag: {button.name}")
            print(f"  Classes: {button.get('class', [])}")
            print(f"  href: {button.get('href', 'N/A')}")
            print(f"  data-toggle: {button.get('data-toggle', 'N/A')}")
            print(f"  data-target: {button.get('data-target', 'N/A')}")
            print(f"  onclick: {button.get('onclick', 'N/A')}")
        
        # Save full HTML for manual inspection
        with open('standings_pagination_debug.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        
        print(f"\n=== Full HTML saved to standings_pagination_debug.html ===")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_pagination_buttons()