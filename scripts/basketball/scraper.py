"""
Basketball Game Log Scraper
============================
This script scrapes game logs from sports-reference.com for college basketball teams.

Flow:
1. Fetch HTML from the game log page
2. Parse the HTML to find the stats table
3. Extract rows of game data
4. Convert to pandas DataFrame
5. Save to CSV

Example URL: https://www.sports-reference.com/cbb/schools/iowa-state/men/2026-gamelogs.html
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import os

def scrape_team_gamelogs(school_slug, year=2026, save_path="data/basketball/raw"):
    """
    Scrape game logs for a single team.
    
    Parameters:
    -----------
    school_slug : str
        The URL slug for the school (e.g., "iowa-state")
    year : int
        The season year (e.g., 2026 for 2025-26 season)
    save_path : str
        Directory to save the CSV file
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing all game logs
    """
    
    # Step 1: Construct the URL
    url = f"https://www.sports-reference.com/cbb/schools/{school_slug}/men/{year}-gamelogs.html"
    print(f"🏀 Scraping {school_slug} game logs from: {url}")
    
    # Step 2: Fetch the webpage
    # We need to set headers to look like a real browser (some sites block bots)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises error for bad status codes (404, 500, etc.)
        print(f"✅ Successfully fetched page (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching page: {e}")
        return None
    
    # Step 3: Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.content, 'lxml')

    # DEBUG: Let's see what tables exist on the page
    print("\n🔍 DEBUG: Looking for tables on the page...")
    all_tables = soup.find_all('table')
    print(f"Found {len(all_tables)} table(s) on the page")

    for i, table in enumerate(all_tables):
        table_id = table.get('id', 'NO_ID')
        table_class = table.get('class', 'NO_CLASS')
        print(f"  Table {i+1}: id='{table_id}', class='{table_class}'")
    
    # Step 4: Find the game log table
    # Sports-reference uses <table id="sgl-basic"> for the game log table
    # table = soup.find('table', {'id': 'sgl-basic'})
    
    # if table is None:
    #     print(f"❌ Could not find game log table on page")
    #     return None
    
    # print(f"✅ Found game log table")
    possible_ids = ['sgl-basic', 'gamelog', 'games', 'schedule']
    table = None

    for table_id in possible_ids:
        table = soup.find('table', {'id': table_id})
        if table:
            print(f"✅ Found table with id='{table_id}'")
            break

    if table is None:
        # Maybe it doesn't have an ID, try finding by class
        table = soup.find('table', class_='stats_table')
        if table:
            print(f"✅ Found table with class='stats_table'")

    if table is None:
        print(f"❌ Could not find game log table on page")
        print(f"💡 Available tables listed above - we may need to adjust our selector")
        return None
    
    # Step 5: Extract table headers (column names)
    headers_row = table.find('thead').find_all('tr')[-1]  # Last row in thead has column names
    headers = [th.get_text(strip=True) for th in headers_row.find_all('th')]
    
    print(f"📊 Columns found: {headers}")
    
    # Step 6: Extract all game rows
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    
    game_data = []
    for row in rows:
        # Skip rows that are section headers (class="thead")
        if 'thead' in row.get('class', []):
            continue
            
        # Extract data from each cell
        cells = row.find_all(['th', 'td'])
        row_data = [cell.get_text(strip=True) for cell in cells]
        
        # Only add rows that have data (some rows might be empty)
        if len(row_data) > 0 and row_data[0]:  # Check if first cell (game number) exists
            game_data.append(row_data)
    
    print(f"✅ Extracted {len(game_data)} games")
    
    # Step 7: Create DataFrame
    df = pd.DataFrame(game_data, columns=headers)
    
    # Step 8: Add metadata columns
    df['school_slug'] = school_slug
    df['season'] = year
    df['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Step 9: Save to CSV
    os.makedirs(save_path, exist_ok=True)
    filename = f"{save_path}/{school_slug}_{year}_gamelogs.csv"
    df.to_csv(filename, index=False)
    print(f"💾 Saved to {filename}")
    
    return df


def scrape_multiple_teams(school_slugs, year=2026, delay=2):
    """
    Scrape game logs for multiple teams.
    
    Parameters:
    -----------
    school_slugs : list
        List of school slugs to scrape
    year : int
        Season year
    delay : int
        Seconds to wait between requests (be polite to the server!)
        
    Returns:
    --------
    dict
        Dictionary mapping school_slug -> DataFrame
    """
    
    all_data = {}
    
    for i, slug in enumerate(school_slugs, 1):
        print(f"\n{'='*60}")
        print(f"Processing team {i}/{len(school_slugs)}: {slug}")
        print(f"{'='*60}")
        
        df = scrape_team_gamelogs(slug, year)
        
        if df is not None:
            all_data[slug] = df
        
        # Be polite - wait between requests to avoid overwhelming the server
        if i < len(school_slugs):
            print(f"⏳ Waiting {delay} seconds before next request...")
            time.sleep(delay)
    
    return all_data


# Test function
if __name__ == "__main__":
    """
    This code runs when you execute the script directly.
    Perfect for testing!
    """
    
    print("🏀 Basketball Game Log Scraper - Test Mode")
    print("=" * 60)
    
    # Test with Iowa State
    test_slug = "iowa-state"
    
    df = scrape_team_gamelogs(test_slug, year=2025)
    
    if df is not None:
        print(f"\n📊 Preview of scraped data:")
        print(df.head(10))
        print(f"\n📈 DataFrame shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")