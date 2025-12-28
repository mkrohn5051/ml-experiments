"""
Transform school names into sports-reference URL slugs.
Handles edge cases like parentheses, special characters, hyphens, etc.
"""

import pandas as pd
import re

def create_slug(school_name):
    """
    Convert school name to sports-reference URL slug.
    
    Examples:
    - "Iowa State" -> "iowa-state"
    - "Albany (NY)" -> "albany"
    - "Arkansas-Pine Bluff" -> "arkansas-pine-bluff"
    - "UC Irvine" -> "uc-irvine"
    - "Saint Mary's (CA)" -> "saint-marys-ca"
    - "Miami (FL)" -> "miami-fl"
    
    Parameters:
    -----------
    school_name : str
        The school name from the list
        
    Returns:
    --------
    str
        The URL slug
    """
    
    slug = school_name
    
    # Handle special cases where parentheses contain state abbreviations
    # These should be kept: "Miami (FL)" -> "miami-fl"
    # These should be removed: "Albany (NY)" -> "albany" (when it's just location)
    
    # Check if parentheses contain a 2-letter state code
    paren_match = re.search(r'\(([A-Z]{2})\)', slug)
    if paren_match:
        state_code = paren_match.group(1)
        # Replace "(FL)" with "-fl" style
        slug = re.sub(r'\s*\([A-Z]{2}\)', f'-{state_code.lower()}', slug)
    else:
        # Remove any other parentheses content (like "(NY)" as location identifier)
        slug = re.sub(r'\s*\([^)]*\)', '', slug)
    
    # Convert to lowercase
    slug = slug.lower()
    
    # Handle possessives: "Saint Mary's" -> "saint-marys"
    slug = slug.replace("'s", "s")
    slug = slug.replace("'", "")
    
    # Handle ampersands: "William & Mary" -> "william-mary"
    slug = slug.replace(' & ', '-')
    
    # Remove periods: "St." -> "st"
    slug = slug.replace('.', '')
    
    # Replace multiple spaces with single hyphen
    slug = re.sub(r'\s+', '-', slug)
    
    # Remove any remaining special characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    # Replace multiple hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug

def process_school_list(input_file, output_file):
    """
    Read school names from ODS file and add slug column.
    
    Parameters:
    -----------
    input_file : str
        Path to input .ods file with 'School' column
    output_file : str
        Path to save output CSV with slugs
    """
    
    print(f"📖 Reading school names from: {input_file}")
    
    # Read the ODS file
    df = pd.read_excel(input_file, engine='odf')
    
    print(f"✅ Found {len(df)} schools")
    print(f"\n📋 Columns in file: {df.columns.tolist()}")
    
    # Create slugs
    print(f"\n🔧 Generating slugs...")
    df['slug'] = df['School'].apply(create_slug)
    
    # Show some examples to verify
    print(f"\n🔍 Sample transformations:")
    print(f"{'School Name':<40s} -> {'Slug':<30s}")
    print("=" * 75)
    
    # Show a variety of examples including tricky ones
    sample_indices = [
        df[df['School'].str.contains('Albany', na=False)].index[0] if len(df[df['School'].str.contains('Albany', na=False)]) > 0 else None,
        df[df['School'].str.contains('Arkansas-Pine', na=False)].index[0] if len(df[df['School'].str.contains('Arkansas-Pine', na=False)]) > 0 else None,
        df[df['School'].str.contains('Miami', na=False)].index[0] if len(df[df['School'].str.contains('Miami', na=False)]) > 0 else None,
        df[df['School'].str.contains("Mary's", na=False)].index[0] if len(df[df['School'].str.contains("Mary's", na=False)]) > 0 else None,
        df[df['School'].str.contains('UC ', na=False)].index[0] if len(df[df['School'].str.contains('UC ', na=False)]) > 0 else None,
    ]
    
    # Remove None values and add some random ones
    sample_indices = [i for i in sample_indices if i is not None]
    sample_indices += df.sample(min(10, len(df))).index.tolist()
    
    for idx in sample_indices[:15]:  # Show first 15
        school = df.loc[idx, 'School']
        slug = df.loc[idx, 'slug']
        print(f"{school:<40s} -> {slug:<30s}")
    
    # Save to CSV
    print(f"\n💾 Saving to: {output_file}")
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Complete! {len(df)} schools with slugs saved.")
    
    return df

if __name__ == "__main__":
    input_file = 'data/basketball/raw/SchoolNames.ods'
    output_file = 'data/basketball/raw/d1_teams.csv'
    
    # Process the file
    teams_df = process_school_list(input_file, output_file)
    
    # Show final stats
    print(f"\n📊 Final Statistics:")
    print(f"   Total teams: {len(teams_df)}")
    print(f"   Unique slugs: {teams_df['slug'].nunique()}")
    
    # Check for any duplicate slugs (shouldn't be any!)
    duplicates = teams_df[teams_df.duplicated('slug', keep=False)]
    if len(duplicates) > 0:
        print(f"\n⚠️  WARNING: Found {len(duplicates)} duplicate slugs:")
        print(duplicates[['School', 'slug']])
    else:
        print(f"   ✅ No duplicate slugs!")