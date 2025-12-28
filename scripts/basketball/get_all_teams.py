"""
Extract all active D1 men's basketball teams from sports-reference
"""

import pandas as pd
import re

def create_slug(school_name):
    """
    Convert school name to URL slug.
    Example: "Iowa State" -> "iowa-state"
    """
    slug = school_name.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[\s]+', '-', slug)     # Replace spaces with hyphens
    slug = re.sub(r'-+', '-', slug)        # Remove duplicate hyphens
    slug = slug.strip('-')                 # Remove leading/trailing hyphens
    
    return slug

def get_all_d1_teams_from_csv():
    """
    Read the schools CSV from sports-reference and extract active D1 teams.
    
    Returns:
    --------
    DataFrame with columns: school_name, slug
    """
    
    # You can paste the CSV data directly or read from a file
    # For now, let's download it
    import requests
    from bs4 import BeautifulSoup
    
    url = "https://www.sports-reference.com/cbb/schools/"
    
    print(f"🏀 Fetching D1 teams list...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    
    # Find the table
    table = soup.find('table', {'id': 'NCAAM_schools'})
    
    if not table:
        print("❌ Could not find table")
        return None
    
    # Read table into pandas
    df = pd.read_html(str(table))[0]
    
    print(f"✅ Found {len(df)} total teams in table")
    
    # Filter for active teams (To year = 2026)
    df_active = df[df['To'] == 2026].copy()
    
    print(f"✅ Filtered to {len(df_active)} active teams (2026 season)")
    
    # Create slugs
    df_active['slug'] = df_active['School'].apply(create_slug)
    
    # Select only needed columns
    teams_df = df_active[['School', 'slug']].copy()
    teams_df.columns = ['school_name', 'slug']
    
    # Sort alphabetically
    teams_df = teams_df.sort_values('school_name').reset_index(drop=True)
    
    return teams_df

if __name__ == "__main__":
    teams_df = get_all_d1_teams_from_csv()
    
    if teams_df is not None:
        # Save to CSV
        import os
        os.makedirs('data/basketball/raw', exist_ok=True)
        teams_df.to_csv('data/basketball/raw/d1_teams.csv', index=False)
        print(f"\n💾 Saved to: data/basketball/raw/d1_teams.csv")
        
        # Show sample
        print(f"\n📋 Sample teams:")
        print(teams_df.head(20))
        
        print(f"\n🏀 Total active D1 teams: {len(teams_df)}")
        
        # Show some random teams to verify slugs
        print(f"\n🔍 Sample slugs:")
        sample = teams_df.sample(10)
        for _, row in sample.iterrows():
            print(f"   {row['school_name']:30s} -> {row['slug']}")