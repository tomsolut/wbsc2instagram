import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
import sys
import argparse
import os
from typing import List, Dict, Optional, Tuple
import logging
import html
import re
import unicodedata

# Try to import selenium for JavaScript rendering
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Try to import requests-html as fallback
try:
    from requests_html import HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False

class WBSCStatscraper:
    def __init__(self, base_url: str, delay: float = 1.0):
        """
        Initialize scraper for WBSC tournament statistics
        
        Args:
            base_url: Base URL of tournament stats page (e.g., .../stats)
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Stats categories we're interested in
        self.stats_categories = ['batting', 'pitching', 'fielding']
        
        # Extract tournament info from URL for better categorization
        self.tournament_info = self._extract_tournament_info(base_url)
        
        # Check available rendering options
        self.js_capable = SELENIUM_AVAILABLE or REQUESTS_HTML_AVAILABLE
        if self.js_capable:
            self.logger.info(f"JavaScript rendering available: Selenium={SELENIUM_AVAILABLE}, requests-html={REQUESTS_HTML_AVAILABLE}")
        else:
            self.logger.warning("No JavaScript rendering available - may have issues with dynamic content")
    
    def _extract_tournament_info(self, url: str) -> Dict:
        """Extract tournament information from URL"""
        try:
            parts = url.split('/')
            tournament_name = None
            
            # Look for tournament identifier in WBSC URLs
            # Pattern: /events/TOURNAMENT-NAME/stats
            for i, part in enumerate(parts):
                if part == 'events' and i + 1 < len(parts):
                    tournament_name = parts[i + 1]
                    break
            
            # Fallback: Look for any part with year and dashes/underscores
            if not tournament_name:
                for part in parts:
                    if '20' in part and ('-' in part or '_' in part):
                        tournament_name = part
                        break
            
            return {
                'name': tournament_name or 'unknown_tournament',
                'url': url,
                'base_domain': url.split('/')[2] if '://' in url else 'unknown'
            }
        except Exception as e:
            self.logger.error(f"Error extracting tournament info: {e}")
            return {'name': 'unknown_tournament', 'url': url, 'base_domain': 'unknown'}
    
    def _fix_text_encoding(self, text: str) -> str:
        """
        Fix text encoding issues commonly found in web scraping
        
        Args:
            text: Raw text that may contain encoding issues
            
        Returns:
            Cleaned text with proper Unicode characters
        """
        if not text or not isinstance(text, str):
            return text
            
        # Common encoding fixes for garbled characters
        fixes = {
            # UTF-8 to Latin-1 corruptions
            '√Å': 'Á',
            '√°': 'á', 
            '√á': 'À',
            '√¢': 'à',
            '√≠': 'í',
            '√∏': 'ï',
            '√ì': 'ì',
            '√ñ': 'Ö',
            '√∂': 'ö',
            '√û': 'Ü',
            '√º': 'ü',
            '√ß': 'ß',
            '√á': 'Ć',
            '√¶': 'ć',
            '√¨': 'È',
            '√®': 'è',
            '√©': 'É',
            '√™': 'é',
            '√≤': 'ò',
            '√≥': 'ó',
            '√Ω': 'Ω',
            '√π': 'π',
            '‚Äô': "'",
            '‚Äú': '"',
            '‚Äù': '"',
            '‚Äì': '–',
            '‚Äî': '—',
            'ƒå': 'Č',
            'ƒÜ': 'ć',
            'ƒ∞': 'ž',
            '≈†': 'Š',
            '≈°': 'š',
            '≈ü': 'Ź',
            '≈∫': 'ź',
            'Ãása': 'ása',
            'NiÃása': 'Niása',
            '√ÅS√°ra': 'ÁSára',
            '√ÅB√°ra': 'ÁBára'
        }
        
        # Apply fixes
        original_text = text
        for wrong, correct in fixes.items():
            text = text.replace(wrong, correct)
        
        # Additional Unicode normalization
        try:
            text = unicodedata.normalize('NFC', text)
        except:
            pass
            
        # Apply name separation logic (surnames are in UPPERCASE, first names in mixed case)
        text = self._separate_name_parts(text)
        
        # Log if we made changes
        if text != original_text:
            self.logger.debug(f"Fixed encoding: '{original_text[:30]}...' -> '{text[:30]}...'")
            
        return text.strip()
    
    def _separate_name_parts(self, name: str) -> str:
        """
        Separate surnames (UPPERCASE) from first names (mixed case)
        
        Args:
            name: Full name string where surname is in UPPERCASE
            
        Returns:
            Name with proper spacing between surname and first names
        """
        if not name or not isinstance(name, str):
            return name
            
        # Use regex to find the pattern: consecutive uppercase letters followed by a capital letter and lowercase
        # This handles cases like: FEKETEAnna -> FEKETE Anna, CAMPIONIAlida -> CAMPIONI Alida
        import re
        
        # Pattern: Find uppercase sequence followed by a capital+lowercase (first name start)
        # (?<=[A-ZÀ-ÿ])(?=[A-ZÀ-ÿ][a-zà-ÿ]) - lookbehind for uppercase, lookahead for Cap+lower
        pattern = r'(?<=[A-ZÀ-ÿ])(?=[A-ZÀ-ÿ][a-zà-ÿ])'
        
                 # Apply the separation
        result = re.sub(pattern, ' ', name)
        
        # Handle special cases where names are already partially separated
        # Example: "FEKETEAnna Ilona" should become "FEKETE Anna Ilona"
        if ' ' in name:
            parts = name.split(' ')
            if len(parts) >= 2:
                # Check if first part needs separation
                first_part = parts[0]
                separated_first = re.sub(pattern, ' ', first_part)
                if separated_first != first_part:
                    result = separated_first + ' ' + ' '.join(parts[1:])
        
        # Fix common over-separation issues with accented characters
        # Example: "ROLFESOVÁ S ára" -> "ROLFESOVÁ Sára"
        result = re.sub(r'([ÁÀÂÄÃÅáàâäãåÉÈÊËéèêëÍÌÎÏíìîïÓÒÔÖÕØóòôöõøÚÙÛÜúùûüÝýÿÇçÑñ]) ([A-Z]) ([a-z])', r'\1 \2\3', result)
        
        return result
    
    def debug_page_structure(self, category: str = 'batting') -> Dict:
        """Debug function to analyze page structure"""
        try:
            target_url = f"{self.base_url}?category={category}" if '?' not in self.base_url else f"{self.base_url}&category={category}"
            self.logger.info(f"Debugging page structure for: {target_url}")
            
            response = self.session.get(target_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            debug_info = {
                'url': target_url,
                'title': soup.title.get_text() if soup.title else 'No title',
                'has_react_data': bool(soup.find('div', {'data-page': True})),
                'tables_found': len(soup.find_all('table')),
                'forms_found': len(soup.find_all('form')),
                'navigation_links': [],
                'table_headers': []
            }
            
            # Check for navigation/pagination
            nav_elements = soup.find_all(['nav', 'div'], class_=lambda x: x and ('nav' in x.lower() or 'page' in x.lower()))
            for nav in nav_elements:
                links = nav.find_all('a')
                debug_info['navigation_links'].extend([{'text': a.get_text(strip=True), 'href': a.get('href')} for a in links])
            
            # Analyze tables
            tables = soup.find_all('table')
            for i, table in enumerate(tables):
                headers = table.find_all(['th', 'td'])[:10]  # First 10 headers
                table_info = {
                    'table_index': i,
                    'headers': [h.get_text(strip=True) for h in headers],
                    'row_count': len(table.find_all('tr'))
                }
                debug_info['table_headers'].append(table_info)
            
            # Check for React data structure
            if debug_info['has_react_data']:
                react_data = self.extract_react_data(target_url)
                if react_data:
                    debug_info['react_data_keys'] = list(react_data.keys())
                    if 'props' in react_data:
                        debug_info['react_props_keys'] = list(react_data['props'].keys())
            
            return debug_info
            
        except Exception as e:
            self.logger.error(f"Error in debug analysis: {e}")
            return {'error': str(e)}
    
    def get_rendered_page(self, url: str) -> BeautifulSoup:
        """Get page content with JavaScript rendered"""
        try:
            if SELENIUM_AVAILABLE:
                return self._get_page_with_selenium(url)
            elif REQUESTS_HTML_AVAILABLE:
                return self._get_page_with_requests_html(url)
            else:
                # Fallback to regular requests
                self.logger.warning("No JavaScript rendering available, using regular requests")
                response = self.session.get(url)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
                
        except Exception as e:
            self.logger.error(f"Error getting rendered page: {e}")
            # Fallback to regular requests
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
    
    def _get_page_with_selenium(self, url: str) -> BeautifulSoup:
        """Use Selenium to get JavaScript-rendered page"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Use webdriver-manager to automatically handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            self.logger.info(f"Loading page with Selenium: {url}")
            driver.get(url)
            
            # Wait for the statistics table to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                self.logger.info("Table found, waiting for data to load...")
                time.sleep(3)  # Give time for data to populate
            except:
                self.logger.warning("No table found or timeout waiting for table")
            
            # Get the page source after JavaScript execution
            page_source = driver.page_source
            return BeautifulSoup(page_source, 'html.parser')
            
        finally:
            driver.quit()
    
    def scrape_all_pages_with_selenium(self, url: str, category: str) -> List[Dict]:
        """Use Selenium to scrape all pages with pagination"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Use webdriver-manager to automatically handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        all_players = []
        
        try:
            self.logger.info(f"Starting paginated scraping for {category}")
            driver.get(url)
            
            # Wait for table to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
                time.sleep(3)
            except:
                self.logger.warning("No table found")
                return []
            
            # First, click on the correct category tab if it exists
            self._select_category_tab(driver, category)
            
            page_num = 1
            max_pages = 20  # Reduced safety limit
            seen_players = set()  # Track seen players to avoid duplicates
            consecutive_duplicate_pages = 0
            
            while page_num <= max_pages:
                self.logger.info(f"Scraping {category} page {page_num}")
                
                # Wait for page to load and get current page data
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extract players from current page
                page_players = self._extract_category_from_page(soup, category)
                
                if not page_players:
                    self.logger.info(f"No players found on page {page_num}, stopping")
                    break
                
                # Check for duplicates
                page_player_keys = set()
                unique_players = []
                
                for player in page_players:
                    player_key = f"{player.get('name', '')}_{player.get('team', '')}"
                    if player_key not in seen_players:
                        seen_players.add(player_key)
                        unique_players.append(player)
                        page_player_keys.add(player_key)
                
                # If no unique players found, we might be at the end or stuck
                if not unique_players:
                    consecutive_duplicate_pages += 1
                    self.logger.warning(f"No unique players on page {page_num} (consecutive duplicates: {consecutive_duplicate_pages})")
                    
                    if consecutive_duplicate_pages >= 3:
                        self.logger.info("Too many consecutive duplicate pages, stopping")
                        break
                else:
                    consecutive_duplicate_pages = 0
                    all_players.extend(unique_players)
                    self.logger.info(f"Found {len(unique_players)} unique players on page {page_num} (total: {len(all_players)})")
                
                # Get pagination info to check if we should continue
                pagination_info = self._get_pagination_info(driver)
                if pagination_info:
                    total_expected = pagination_info.get('total', 0)
                    if len(all_players) >= total_expected:
                        self.logger.info(f"Reached expected total of {total_expected} players")
                        break
                
                # Check if there's a next page and navigate to it
                if not self._navigate_to_next_page(driver, page_num):
                    self.logger.info("No more pages available")
                    break
                
                page_num += 1
                time.sleep(self.delay)
            
            self.logger.info(f"Finished scraping {category}. Total players: {len(all_players)}")
            return all_players
            
        except Exception as e:
            self.logger.error(f"Error during paginated scraping: {e}")
            return all_players
            
        finally:
            driver.quit()
    
    def _select_category_tab(self, driver, category: str):
        """Select the correct category tab (Batting/Pitching/Fielding)"""
        try:
            # Look for category tabs/buttons
            category_buttons = [
                f"//button[contains(text(), '{category.title()}')]",
                f"//a[contains(text(), '{category.title()}')]",
                f"//*[contains(@class, 'tab') and contains(text(), '{category.title()}')]",
                f"//*[contains(text(), '{category.title()}')]"
            ]
            
            for xpath in category_buttons:
                try:
                    button = driver.find_element(By.XPATH, xpath)
                    if button.is_displayed():
                        self.logger.info(f"Clicking {category} tab")
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(2)
                        return True
                except:
                    continue
            
            self.logger.info(f"No specific {category} tab found - using default view")
            return False
            
        except Exception as e:
            self.logger.warning(f"Error selecting category tab: {e}")
            return False
    
    def _navigate_to_next_page(self, driver, current_page: int) -> bool:
        """Navigate to the next page using pagination controls"""
        try:
            # Strategy 1: Look for "Next" button
            next_selectors = [
                "//a[contains(text(), 'Next')]",
                "//button[contains(text(), 'Next')]", 
                "//*[contains(@class, 'next')]",
                "//a[contains(@class, 'page-link') and contains(text(), 'Next')]"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = driver.find_element(By.XPATH, selector)
                    if next_button.is_enabled() and next_button.is_displayed():
                        self.logger.info("Clicking Next button")
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)
                        return True
                except:
                    continue
            
            # Strategy 2: Look for specific page number
            next_page = current_page + 1
            page_selectors = [
                f"//a[contains(text(), '{next_page}')]",
                f"//button[contains(text(), '{next_page}')]",
                f"//*[contains(@class, 'page-link') and text()='{next_page}']"
            ]
            
            for selector in page_selectors:
                try:
                    page_button = driver.find_element(By.XPATH, selector)
                    if page_button.is_enabled() and page_button.is_displayed():
                        self.logger.info(f"Clicking page {next_page} button")
                        driver.execute_script("arguments[0].click();", page_button)
                        time.sleep(3)
                        return True
                except:
                    continue
            
            # Strategy 3: Check pagination info to see if we can continue
            pagination_info = self._get_pagination_info(driver)
            if pagination_info:
                current_shown = pagination_info.get('current_end', 0)
                total_entries = pagination_info.get('total', 0)
                if current_shown < total_entries:
                    self.logger.warning(f"More pages available ({current_shown}/{total_entries}) but navigation failed")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error navigating to next page: {e}")
            return False
    
    def _get_pagination_info(self, driver) -> Dict:
        """Extract pagination information from the page"""
        try:
            # Look for pagination info like "Showing 1 to 25 of 269 entries"
            info_patterns = [
                "//div[contains(text(), 'Showing')]",
                "//*[contains(text(), 'entries')]",
                "//*[contains(text(), 'of') and contains(text(), 'entries')]"
            ]
            
            for pattern in info_patterns:
                try:
                    info_element = driver.find_element(By.XPATH, pattern)
                    info_text = info_element.text
                    
                    # Parse text like "Showing 1 to 25 of 269 entries"
                    import re
                    match = re.search(r'Showing\s+(\d+)\s+to\s+(\d+)\s+of\s+(\d+)\s+entries', info_text)
                    if match:
                        return {
                            'current_start': int(match.group(1)),
                            'current_end': int(match.group(2)),
                            'total': int(match.group(3))
                        }
                except:
                    continue
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting pagination info: {e}")
            return {}
    
    def _get_page_with_requests_html(self, url: str) -> BeautifulSoup:
        """Use requests-html to get JavaScript-rendered page"""
        session = HTMLSession()
        
        self.logger.info(f"Loading page with requests-html: {url}")
        r = session.get(url)
        
        # Render JavaScript
        r.html.render(timeout=20, wait=3)
        
        return BeautifulSoup(r.html.html, 'html.parser')
    
    def extract_react_data(self, url: str = None) -> Optional[Dict]:
        """Extract the React data from the WBSC page"""
        try:
            target_url = url or self.base_url
            response = self.session.get(target_url)
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
                
                return page_data
            else:
                self.logger.error("No data-page div found")
                return None
                
        except Exception as e:
            self.logger.error(f"Error extracting React data: {e}")
            return None
    
    def scrape_all_stats(self, categories: List[str] = None) -> Dict[str, List[Dict]]:
        """Scrape all statistics categories (batting, pitching, fielding)"""
        if categories is None:
            categories = self.stats_categories
        
        all_stats = {}
        
        # For WBSC sites, often all categories show the same data (batting stats)
        # So we'll scrape batting first and check if other categories are different
        
        first_category = categories[0]
        self.logger.info(f"Scraping {first_category} statistics...")
        first_stats = self._scrape_category_stats(first_category)
        all_stats[first_category] = first_stats
        
        # Skip other categories if we only want one or if requested
        if len(categories) == 1:
            return all_stats
        
        for category in categories[1:]:
            self.logger.info(f"Scraping {category} statistics...")
            category_stats = self._scrape_category_stats(category)
            
            # Check if this is identical to batting stats (common on WBSC sites)
            if category_stats and first_stats and len(category_stats) == len(first_stats):
                # Simple check: if same number of players and first player has same name
                if (category_stats[0].get('name') == first_stats[0].get('name') and
                    category_stats[0].get('team') == first_stats[0].get('team')):
                    self.logger.info(f"{category} appears to contain same data as {first_category}, reusing data")
                    all_stats[category] = first_stats
                    continue
            
            all_stats[category] = category_stats
            time.sleep(self.delay)
        
        return all_stats
    
    def _scrape_category_stats(self, category: str) -> List[Dict]:
        """Scrape statistics for a specific category (batting/pitching/fielding) with pagination"""
        try:
            self.logger.info(f"Scraping {category} statistics with pagination support")
            
            # Get the main stats page URL
            base_url = self.base_url.split('?')[0]  # Remove any existing parameters
            
            # Use JavaScript-capable rendering with pagination if available
            if SELENIUM_AVAILABLE:
                self.logger.info("Using Selenium for paginated scraping")
                players = self.scrape_all_pages_with_selenium(base_url, category)
            elif self.js_capable:
                self.logger.info("Using JavaScript-capable rendering (single page)")
                soup = self.get_rendered_page(base_url)
                players = self._extract_category_from_page(soup, category)
            else:
                self.logger.info("Using regular HTTP request (single page)")
                response = self.session.get(base_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                players = self._extract_category_from_page(soup, category)
            
            self.logger.info(f"Total {category} players scraped: {len(players)}")
            return players
            
        except Exception as e:
            self.logger.error(f"Error scraping {category} stats: {e}")
            return []
    
    def _extract_category_from_page(self, soup, category: str) -> List[Dict]:
        """Extract players for a specific category from the page"""
        try:
            players = []
            
            # Method 1: Look for category tabs and tables
            # Find batting/pitching/fielding tabs or sections
            category_buttons = soup.find_all(['button', 'a', 'div'], 
                                           string=lambda text: text and category.lower() in text.lower())
            
            self.logger.info(f"Found {len(category_buttons)} potential {category} buttons/tabs")
            
            # Method 2: Look for all tables and try to identify which one contains the category data
            tables = soup.find_all('table')
            self.logger.info(f"Found {len(tables)} tables on page")
            
            for i, table in enumerate(tables):
                self.logger.info(f"Analyzing table {i} for {category} data")
                
                # Check if table contains category-specific data
                if self._table_contains_category_data(table, category):
                    self.logger.info(f"Table {i} appears to contain {category} data")
                    table_players = self._extract_players_from_stats_table(table, category)
                    players.extend(table_players)
                    
                    # For now, take the first matching table
                    if players:
                        break
            
            # Method 3: If no specific table found, try the largest/main table
            if not players and tables:
                self.logger.info(f"No specific {category} table found, trying main table")
                main_table = max(tables, key=lambda t: len(t.find_all('tr')))
                players = self._extract_players_from_stats_table(main_table, category)
            
            return players
            
        except Exception as e:
            self.logger.error(f"Error extracting {category} from page: {e}")
            return []
    
    def _table_contains_category_data(self, table, category: str) -> bool:
        """Check if a table contains data for the specified category"""
        try:
            # Get all text from the table
            table_text = table.get_text().lower()
            
            # Category-specific indicators
            if category == 'batting':
                indicators = ['avg', 'hits', 'runs', 'rbi', 'ab', 'batting average', 'home runs', 'slg', 'obp', 'ops']
            elif category == 'pitching':
                indicators = ['era', 'wins', 'losses', 'innings', 'strikeouts', 'earned run', 'ip', 'whip', 'er']
            elif category == 'fielding':
                indicators = ['errors', 'assists', 'putouts', 'fielding%', 'fielding percentage', 'po', 'fpct']
            else:
                indicators = []
            
            # Check if table contains category indicators
            has_indicators = any(indicator in table_text for indicator in indicators)
            
            # Also check if table has player/team columns
            has_players = any(term in table_text for term in ['player', 'team', 'name'])
            
            # For batting, we always return True if it has players (since batting is default view)
            if category == 'batting' and has_players:
                return True
            
            # Must have both players and category-specific stats
            return has_indicators and has_players
            
        except Exception as e:
            self.logger.error(f"Error checking table content: {e}")
            return False
    
    def _extract_players_from_stats_table(self, table, category: str) -> List[Dict]:
        """Extract player statistics from a WBSC stats table"""
        try:
            players = []
            
            # Find all rows
            rows = table.find_all('tr')
            if not rows:
                self.logger.warning("No rows found in table")
                return []
            
            self.logger.info(f"Found {len(rows)} rows in table")
            
            # Find header row by looking for typical column names
            headers = []
            header_row_index = -1
            
            for i, row in enumerate(rows[:5]):  # Check first 5 rows for headers
                cells = row.find_all(['th', 'td'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # Check if this looks like a header row
                header_indicators = ['player', 'team', 'g', 'ab', 'avg', 'era', 'w', 'l']
                if any(indicator.lower() in [text.lower() for text in cell_texts] for indicator in header_indicators):
                    headers = cell_texts
                    header_row_index = i
                    self.logger.info(f"Found headers in row {i}: {headers}")
                    break
            
            # If no clear headers found, try to use the first row
            if not headers and rows:
                first_row_cells = rows[0].find_all(['th', 'td'])
                headers = [cell.get_text(strip=True) for cell in first_row_cells]
                header_row_index = 0
                self.logger.info(f"Using first row as headers: {headers}")
            
            if not headers:
                self.logger.warning("No headers found")
                return []
            
            # Process data rows (skip header row)
            data_rows = rows[header_row_index + 1:] if header_row_index >= 0 else rows[1:]
            
            for row_idx, row in enumerate(data_rows):
                cells = row.find_all(['td', 'th'])
                
                if len(cells) < 2:  # Need at least player and team
                    continue
                
                # Extract cell values - keep headers as-is from frontend
                player_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        header = headers[i].strip()  # Keep original casing
                        value = cell.get_text(strip=True)
                        
                        if value and value not in ['-', '', '—', 'N/A']:
                            player_data[header] = value  # Use original header as key
                
                # Process the player if we have enough data
                if len(player_data) >= 2:
                    processed_player = self._process_frontend_headers_player_data(player_data, category)
                    if processed_player:
                        players.append(processed_player)
                        
                        # Log first few players for debugging
                        if row_idx < 3:
                            player_name = processed_player.get('name', 'Unknown')
                            team = processed_player.get('team', 'Unknown')
                            self.logger.info(f"Processed player {row_idx + 1}: {player_name} ({team})")
            
            self.logger.info(f"Successfully extracted {len(players)} players from stats table")
            return players
            
        except Exception as e:
            self.logger.error(f"Error extracting from stats table: {e}")
            return []
    
    def _process_wbsc_player_data(self, player_data: Dict, category: str) -> Optional[Dict]:
        """Process player data specifically for WBSC format"""
        try:
            processed_player = {
                'category': category,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Enhanced field mappings for WBSC format
            field_mappings = {
                'name': ['player', 'name', 'player name'],
                'team': ['team', 'club', 'country'],
                'games': ['g', 'games', 'gp'],
                'at_bats': ['ab', 'at bats'],
                'runs': ['r', 'runs'],
                'hits': ['h', 'hits'],
                'doubles': ['2b', 'doubles', '2-base hits'],
                'triples': ['3b', 'triples', '3-base hits'],
                'home_runs': ['hr', 'home runs', 'home_runs'],
                'rbi': ['rbi', 'runs batted in'],
                'total_bases': ['tb', 'total bases'],
                'batting_average': ['avg', 'ba', 'batting average'],
                'slugging_percentage': ['slg', 'slugging', 'slugging percentage'],
                'on_base_percentage': ['obp', 'on base', 'on base percentage'],
                'ops': ['ops', 'on base plus slugging'],
                'walks': ['bb', 'walks', 'base on balls'],
                'hit_by_pitch': ['hbp', 'hit by pitch'],
                'strikeouts': ['so', 'strikeouts', 'strike outs'],
                'sacrifice_hits': ['sh', 'sacrifice hits'],
                'sacrifice_flies': ['sf', 'sacrifice flies'],
                'grounded_into_double_play': ['gdp', 'double plays'],
                # Pitching stats
                'wins': ['w', 'wins'],
                'losses': ['l', 'losses'],
                'saves': ['sv', 'saves'],
                'innings_pitched': ['ip', 'innings pitched', 'innings'],
                'hits_allowed': ['h', 'hits allowed'],
                'runs_allowed': ['r', 'runs allowed'],
                'earned_runs': ['er', 'earned runs'],
                'walks_allowed': ['bb', 'walks allowed'],
                'strikeouts_pitched': ['so', 'strikeouts'],
                'era': ['era', 'earned run average'],
                # Fielding stats
                'putouts': ['po', 'putouts'],
                'assists': ['a', 'assists'],
                'errors': ['e', 'errors'],
                'fielding_percentage': ['fpct', 'fielding%', 'fielding percentage']
            }
            
            # Extract player info using case-insensitive field mappings
            for field, possible_names in field_mappings.items():
                for name in possible_names:
                    if name in player_data:
                        value = player_data[name]
                        # Fix text encoding for string fields
                        if isinstance(value, str) and field in ['name', 'team']:
                            value = self._fix_text_encoding(value)
                        processed_player[field] = value
                        break
            
            # Ensure we have essential fields
            if not processed_player.get('name'):
                return None
                
            return processed_player
            
        except Exception as e:
            self.logger.error(f"Error processing WBSC player data: {e}")
            return None
    
    def _process_frontend_headers_player_data(self, player_data: Dict, category: str) -> Optional[Dict]:
        """Process player data using exact frontend headers (no field mapping)"""
        try:
            processed_player = {
                'category': category,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Copy all data with original headers, applying text encoding fixes only to string fields
            for header, value in player_data.items():
                # Fix text encoding for likely text fields (Player, Team)
                if isinstance(value, str) and header in ['Player', 'Team']:
                    value = self._fix_text_encoding(value)
                processed_player[header] = value
            
            # Ensure we have essential fields (Player is required)
            if not processed_player.get('Player'):
                self.logger.warning(f"No Player field found in: {list(player_data.keys())}")
                return None
                
            return processed_player
            
        except Exception as e:
            self.logger.error(f"Error processing frontend headers player data: {e}")
            return None
    
    def _extract_players_from_page(self, page_data: Dict, category: str) -> List[Dict]:
        """Extract player statistics from a single page"""
        try:
            players = []
            
            # If we have React data, try to extract from it first
            if page_data:
                props = page_data.get('props', {})
                
                # Look for stats data in various possible locations
                stats_data = None
                
                # Try different possible data locations
                if 'stats' in props:
                    stats_data = props['stats']
                elif 'players' in props:
                    stats_data = props['players']
                elif f'{category}_stats' in props:
                    stats_data = props[f'{category}_stats']
                elif 'data' in props:
                    stats_data = props['data']
                
                # Process React data if found
                if stats_data and isinstance(stats_data, list):
                    for player_data in stats_data:
                        processed_player = self._process_player_data(player_data, category)
                        if processed_player:
                            players.append(processed_player)
                    
                    if players:
                        self.logger.info(f"Extracted {len(players)} players from React data")
                        return players
            
            # If no React data or no players found, try HTML extraction
            self.logger.info("No React data found or no players extracted, trying HTML extraction")
            html_players = self._extract_players_from_html(page_data, category)
            
            return html_players
            
        except Exception as e:
            self.logger.error(f"Error extracting players from page: {e}")
            # Fallback to HTML extraction even on error
            try:
                return self._extract_players_from_html(page_data, category)
            except:
                return []
    
    def _extract_players_from_html(self, page_data: Dict, category: str) -> List[Dict]:
        """Fallback method to extract stats from HTML tables"""
        try:
            self.logger.info("Attempting HTML table extraction as fallback")
            
            # We need to re-fetch the page without category parameter first
            base_url = self.base_url.split('?')[0]  # Remove any existing parameters
            response = self.session.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for stats tables in various containers
            players = []
            
            # Method 1: Look for all tables
            tables = soup.find_all('table')
            self.logger.info(f"Found {len(tables)} tables on page")
            
            for i, table in enumerate(tables):
                self.logger.info(f"Analyzing table {i}")
                
                # Try to extract data from any table that might contain stats
                table_players = self._extract_players_from_table(table, category)
                if table_players:
                    self.logger.info(f"Found {len(table_players)} players in table {i}")
                    players.extend(table_players)
            
            # Method 2: Look for specific containers that might hold stats
            stat_containers = soup.find_all(['div', 'section'], class_=lambda x: x and ('stat' in x.lower() or 'table' in x.lower()))
            
            for container in stat_containers:
                container_tables = container.find_all('table')
                for table in container_tables:
                    table_players = self._extract_players_from_table(table, category)
                    players.extend(table_players)
            
            # Method 3: Look for tbody elements directly
            tbodies = soup.find_all('tbody')
            for tbody in tbodies:
                # Create a temporary table structure
                temp_table = soup.new_tag('table')
                temp_table.append(tbody)
                table_players = self._extract_players_from_table(temp_table, category)
                players.extend(table_players)
            
            self.logger.info(f"Total players extracted from HTML: {len(players)}")
            return players
            
        except Exception as e:
            self.logger.error(f"Error in HTML extraction: {e}")
            return []
    
    def _is_stats_table(self, table, category: str) -> bool:
        """Check if a table contains statistics for the given category"""
        try:
            # Look for column headers that indicate stats
            headers = table.find_all(['th', 'td'])
            header_text = ' '.join([h.get_text().lower() for h in headers[:10]])  # First few headers
            
            # Category-specific indicators
            if category == 'batting':
                indicators = ['avg', 'hits', 'runs', 'rbi', 'at bat', 'average']
            elif category == 'pitching':
                indicators = ['era', 'wins', 'losses', 'innings', 'strikeouts', 'earned run']
            elif category == 'fielding':
                indicators = ['errors', 'assists', 'putouts', 'fielding%', 'fielding percentage']
            else:
                indicators = []
            
            return any(indicator in header_text for indicator in indicators)
            
        except Exception as e:
            self.logger.error(f"Error checking if table is stats table: {e}")
            return False
    
    def _extract_players_from_table(self, table, category: str) -> List[Dict]:
        """Extract player statistics from an HTML table"""
        try:
            players = []
            
            # Find header row - try multiple methods
            headers = []
            
            # Method 1: Look for thead
            thead = table.find('thead')
            if thead:
                header_cells = thead.find_all(['th', 'td'])
                headers = [th.get_text(strip=True).lower() for th in header_cells if th.get_text(strip=True)]
                self.logger.info(f"Found headers in thead: {headers[:5]}...")  # Show first 5
            
            # Method 2: Try first row as headers if no thead found
            if not headers:
                all_rows = table.find_all('tr')
                if all_rows:
                    first_row = all_rows[0]
                    header_cells = first_row.find_all(['th', 'td'])
                    headers = [th.get_text(strip=True).lower() for th in header_cells if th.get_text(strip=True)]
                    self.logger.info(f"Found headers in first row: {headers[:5]}...")  # Show first 5
            
            # Method 3: Look for any row with typical header text
            if not headers:
                for row in table.find_all('tr')[:3]:  # Check first 3 rows
                    cells = row.find_all(['th', 'td'])
                    cell_texts = [cell.get_text(strip=True).lower() for cell in cells]
                    # Check if this looks like a header row (contains common stat terms)
                    if any(term in ' '.join(cell_texts) for term in ['player', 'team', 'avg', 'era', 'games', 'hits', 'runs']):
                        headers = cell_texts
                        self.logger.info(f"Found headers by pattern matching: {headers[:5]}...")
                        break
            
            if not headers:
                self.logger.warning("No headers found in table")
                return []
            
            # Find data rows
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                self.logger.info(f"Found {len(rows)} data rows in tbody")
            else:
                all_rows = table.find_all('tr')
                # Skip the header row (first row)
                rows = all_rows[1:] if len(all_rows) > 1 else []
                self.logger.info(f"Found {len(rows)} data rows (skipped header)")
            
            for row_idx, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:  # At least player and team
                    player_data = {}
                    
                    # Map cell values to headers
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            cell_text = cell.get_text(strip=True)
                            # Clean up the cell text
                            if cell_text and cell_text not in ['-', '', '—']:
                                player_data[headers[i]] = cell_text
                    
                    # Process the player data if we have enough information
                    if len(player_data) >= 2:  # At least 2 fields
                        processed_player = self._process_html_player_data(player_data, category)
                        if processed_player:
                            players.append(processed_player)
                            if row_idx < 3:  # Log first few players for debugging
                                self.logger.info(f"Processed player: {processed_player.get('name', 'Unknown')}")
            
            self.logger.info(f"Extracted {len(players)} players from table")
            return players
            
        except Exception as e:
            self.logger.error(f"Error extracting players from table: {e}")
            return []
    
    def _process_html_player_data(self, player_data: Dict, category: str) -> Optional[Dict]:
        """Process player data extracted from HTML tables"""
        try:
            processed_player = {
                'category': category,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Map common field names (case-insensitive)
            field_mappings = {
                'name': ['name', 'player', 'player name', 'player_name', 'playername'],
                'team': ['team', 'club', 'team name', 'team_name', 'teamname'],
                'number': ['no', 'num', 'number', '#', 'jersey', 'jersey_number'],
                'games': ['g', 'games', 'gp', 'games played', 'games_played'],
                'at_bats': ['ab', 'at bats', 'atbats', 'at_bats'],
                'runs': ['r', 'runs'],
                'hits': ['h', 'hits'],
                'rbi': ['rbi', 'runs batted in', 'runs_batted_in'],
                'batting_average': ['avg', 'ba', 'batting average', 'batting_average', 'battingaverage'],
                'era': ['era', 'earned run average', 'earned_run_average'],
                'wins': ['w', 'wins'],
                'losses': ['l', 'losses'],
                'errors': ['e', 'errors'],
                'assists': ['a', 'assists'],
                'putouts': ['po', 'putouts']
            }
            
            # Extract player info using field mappings (case-insensitive)
            player_data_lower = {k.lower(): v for k, v in player_data.items()}
            
            for field, possible_names in field_mappings.items():
                for name in possible_names:
                    if name.lower() in player_data_lower:
                        value = player_data_lower[name.lower()]
                        # Fix text encoding for string fields
                        if isinstance(value, str) and field in ['name', 'team']:
                            value = self._fix_text_encoding(value)
                        processed_player[field] = value
                        break
            
            # Ensure we have at least a name
            if not processed_player.get('name'):
                return None
                
            return processed_player
            
        except Exception as e:
            self.logger.error(f"Error processing HTML player data: {e}")
            return None
    
    def _process_player_data(self, player_data: Dict, category: str) -> Optional[Dict]:
        """Process individual player statistics data"""
        try:
            processed_player = {
                'category': category,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract common player info
            player_name = player_data.get('name', player_data.get('player_name', 'Unknown'))
            team_name = player_data.get('team', player_data.get('team_name', 'Unknown'))
            
            # Fix text encoding
            processed_player['player_name'] = self._fix_text_encoding(player_name) if isinstance(player_name, str) else player_name
            processed_player['team'] = self._fix_text_encoding(team_name) if isinstance(team_name, str) else team_name
            processed_player['jersey_number'] = player_data.get('number', player_data.get('jersey_number'))
            
            # Extract category-specific statistics
            if category == 'batting':
                processed_player.update(self._extract_batting_stats(player_data))
            elif category == 'pitching':
                processed_player.update(self._extract_pitching_stats(player_data))
            elif category == 'fielding':
                processed_player.update(self._extract_fielding_stats(player_data))
            
            return processed_player
            
        except Exception as e:
            self.logger.error(f"Error processing player data: {e}")
            return None
    
    def _extract_batting_stats(self, player_data: Dict) -> Dict:
        """Extract batting statistics"""
        batting_stats = {}
        
        # Common batting statistics
        batting_fields = [
            'games', 'at_bats', 'runs', 'hits', 'doubles', 'triples', 
            'home_runs', 'rbi', 'walks', 'strikeouts', 'stolen_bases',
            'batting_average', 'on_base_percentage', 'slugging_percentage',
            'ops', 'sacrifice_hits', 'sacrifice_flies', 'hit_by_pitch'
        ]
        
        for field in batting_fields:
            # Try different possible field names
            value = (player_data.get(field) or 
                    player_data.get(field.upper()) or
                    player_data.get(field.replace('_', '')) or
                    player_data.get(field.replace('_', ' ').title().replace(' ', '')))
            
            if value is not None:
                batting_stats[field] = value
        
        return batting_stats
    
    def _extract_pitching_stats(self, player_data: Dict) -> Dict:
        """Extract pitching statistics"""
        pitching_stats = {}
        
        # Common pitching statistics
        pitching_fields = [
            'games', 'games_started', 'complete_games', 'shutouts',
            'wins', 'losses', 'saves', 'innings_pitched', 'hits_allowed',
            'runs_allowed', 'earned_runs', 'walks_allowed', 'strikeouts',
            'home_runs_allowed', 'era', 'whip', 'batting_average_against'
        ]
        
        for field in pitching_fields:
            # Try different possible field names
            value = (player_data.get(field) or 
                    player_data.get(field.upper()) or
                    player_data.get(field.replace('_', '')) or
                    player_data.get(field.replace('_', ' ').title().replace(' ', '')))
            
            if value is not None:
                pitching_stats[field] = value
        
        return pitching_stats
    
    def _extract_fielding_stats(self, player_data: Dict) -> Dict:
        """Extract fielding statistics"""
        fielding_stats = {}
        
        # Common fielding statistics
        fielding_fields = [
            'games', 'games_started', 'innings_played', 'putouts',
            'assists', 'errors', 'double_plays', 'fielding_percentage',
            'range_factor', 'passed_balls', 'stolen_bases_against',
            'caught_stealing', 'pickoffs'
        ]
        
        for field in fielding_fields:
            # Try different possible field names
            value = (player_data.get(field) or 
                    player_data.get(field.upper()) or
                    player_data.get(field.replace('_', '')) or
                    player_data.get(field.replace('_', ' ').title().replace(' ', '')))
            
            if value is not None:
                fielding_stats[field] = value
        
        return fielding_stats
    
    def _has_next_page(self, page_data: Dict) -> bool:
        """Check if there's a next page available"""
        try:
            props = page_data.get('props', {})
            
            # Look for pagination info
            pagination = props.get('pagination', {})
            if pagination:
                current_page = pagination.get('current_page', 1)
                total_pages = pagination.get('total_pages', 1)
                return current_page < total_pages
            
            # Alternative: check if current page has data
            # If we found players, assume there might be more
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking for next page: {e}")
            return False
    
    def save_results(self, stats_data: Dict[str, List[Dict]], output_path: str = None, tournament_name: str = None):
        """Save scraped statistics data to files"""
        try:
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                if tournament_name and tournament_name != 'tournament':
                    tournament_slug = tournament_name.lower().replace(' ', '_').replace('-', '_')
                    # Use central outputs directory with stats suffix
                    output_path = f"../outputs/{datetime.now().strftime('%Y-%m-%d')}_{tournament_slug}__complete_stats"
                else:
                    # Fallback for unknown tournaments
                    output_path = f"../outputs/{datetime.now().strftime('%Y-%m-%d')}_tournament_stats"
            
            os.makedirs(output_path, exist_ok=True)
            
            # Save complete stats data
            timestamp = datetime.now().strftime('%H%M%S')
            
            # Save JSON
            json_file = f"{output_path}/stats_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
            # Save CSV for each category
            for category, players in stats_data.items():
                if players:
                    df = pd.DataFrame(players)
                    csv_file = f"{output_path}/stats_{category}_{timestamp}.csv"
                    df.to_csv(csv_file, index=False, encoding='utf-8')
                    self.logger.info(f"Saved {len(players)} {category} records to {csv_file}")
            
            self.logger.info(f"All statistics saved to {output_path}")
            
            # Print summary
            total_players = sum(len(players) for players in stats_data.values())
            print(f"\n📊 Scraping Summary:")
            print(f"Total player records: {total_players}")
            for category, players in stats_data.items():
                print(f"  - {category.capitalize()}: {len(players)} players")
            print(f"Files saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")


def main():
    parser = argparse.ArgumentParser(description='Scrape WBSC Tournament Statistics')
    parser.add_argument('--url', required=True, help='Tournament stats URL')
    parser.add_argument('--output', help='Output directory path')
    parser.add_argument('--tournament-name', help='Tournament name for file naming')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode to analyze page structure')
    parser.add_argument('--category', default='batting', help='Category for debug mode (batting/pitching/fielding)')
    parser.add_argument('--categories', nargs='+', default=['batting', 'pitching', 'fielding'], 
                       help='Categories to scrape (batting, pitching, fielding)')
    parser.add_argument('--batting-only', action='store_true', help='Only scrape batting statistics')
    
    args = parser.parse_args()
    
    scraper = WBSCStatscraper(args.url, args.delay)
    
    if args.debug:
        print(f"🔍 Debug-Modus: Analysiere Seitenstruktur für {args.url}")
        debug_info = scraper.debug_page_structure(args.category)
        
        print("\n📊 Debug-Informationen:")
        print(f"URL: {debug_info.get('url')}")
        print(f"Titel: {debug_info.get('title')}")
        print(f"React-Daten verfügbar: {debug_info.get('has_react_data')}")
        print(f"Tabellen gefunden: {debug_info.get('tables_found')}")
        print(f"Formulare gefunden: {debug_info.get('forms_found')}")
        
        if debug_info.get('table_headers'):
            print("\n📋 Tabellen-Struktur:")
            for table_info in debug_info['table_headers']:
                print(f"  Tabelle {table_info['table_index']}: {table_info['row_count']} Zeilen")
                print(f"    Headers: {table_info['headers'][:5]}...")  # Show first 5 headers
        
        if debug_info.get('navigation_links'):
            print(f"\n🔗 Navigation gefunden: {len(debug_info['navigation_links'])} Links")
        
        if debug_info.get('react_data_keys'):
            print(f"\n⚛️ React-Daten Schlüssel: {debug_info['react_data_keys']}")
            if debug_info.get('react_props_keys'):
                print(f"Props Schlüssel: {debug_info['react_props_keys']}")
        
        # Save debug info
        import json
        debug_file = f"debug_stats_{args.category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Debug-Informationen gespeichert in: {debug_file}")
        
        return
    
    # Determine which categories to scrape
    if args.batting_only:
        categories_to_scrape = ['batting']
        print(f"🏆 Starte Statistik-Scraping für: {args.url}")
        print("📊 Kategorie: Nur Batting")
    else:
        categories_to_scrape = args.categories
        print(f"🏆 Starte Statistik-Scraping für: {args.url}")
        print(f"📊 Kategorien: {', '.join(categories_to_scrape).title()}")
    
    # Scrape statistics
    stats_data = scraper.scrape_all_stats(categories_to_scrape)
    
    # Save results - use extracted tournament name if available
    tournament_name = args.tournament_name or scraper.tournament_info.get('name', 'tournament')
    scraper.save_results(stats_data, args.output, tournament_name)


if __name__ == "__main__":
    main() 