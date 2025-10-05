"""
Satellite Catalog Scraper
Fetches satellite data from planet4589.org and creates a master CSV list
"""

import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime

def fetch_satcat_html():
    """Fetch the satellite catalog HTML from planet4589.org"""
    url = "https://planet4589.org/space/gcat/data/cat/satcat.html"
    
    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print(f"✓ Successfully fetched data ({len(response.content)} bytes)")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching data: {e}")
        return None

def parse_satcat_table(html_content):
    """Parse the HTML PRE tag and extract satellite data using fixed-width columns"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all PRE tags
    pre_tags = soup.find_all('pre')
    if not pre_tags:
        print("✗ Could not find PRE tags in HTML")
        return None
    
    print(f"Found {len(pre_tags)} PRE tags")
    
    # The first PRE tag contains the header
    header_text = pre_tags[0].get_text()
    header_line = header_text.strip()
    
    # Parse headers and determine column positions
    headers = []
    col_positions = []
    current_pos = 0
    
    # Split by multiple spaces to get column headers
    import re
    header_parts = re.split(r'\s{2,}', header_line)
    
    for header in header_parts:
        if header.strip():
            headers.append(header.strip())
            # Find position in original line
            pos = header_line.find(header, current_pos)
            col_positions.append(pos)
            current_pos = pos + len(header)
    
    # Add end position for last column
    col_positions.append(len(header_line))
    
    print(f"Found {len(headers)} headers: {headers[:10]}... (showing first 10)")
    
    # The data is in the subsequent PRE tags
    rows = []
    for pre_tag in pre_tags[1:]:  # Skip first PRE (header)
        text = pre_tag.get_text()
        lines = text.strip().split('\n')
        
        for line in lines:
            # Skip comment lines and empty lines
            if line.startswith('#') or not line.strip():
                continue
            
            # Skip if line doesn't start with 'S' (satellite entries start with S)
            if not line.startswith('S'):
                continue
            
            # Parse using column positions
            row_data = []
            for i in range(len(col_positions) - 1):
                start = col_positions[i]
                end = col_positions[i + 1]
                # Handle lines shorter than expected
                if start < len(line):
                    value = line[start:end].strip() if end <= len(line) else line[start:].strip()
                    row_data.append(value if value else '-')
                else:
                    row_data.append('-')
            
            if len(row_data) > 0:
                rows.append(row_data)
    
    print(f"✓ Extracted {len(rows)} satellite entries")
    return headers, rows

def save_to_csv(headers, rows, filename='data/satcat_master.csv'):
    """Save the parsed data to CSV"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"✓ Saved {len(rows)} entries to {filename}")
        return True
    except Exception as e:
        print(f"✗ Error saving CSV: {e}")
        return False

def load_active_satellites(active_csv='data/active-20251004.csv'):
    """Load the active satellites list"""
    try:
        df = pd.read_csv(active_csv)
        print(f"✓ Loaded {len(df)} active satellites from {active_csv}")
        return df
    except Exception as e:
        print(f"✗ Error loading active satellites: {e}")
        return None

def create_master_list(satcat_csv='data/satcat_master.csv', 
                       active_csv='data/active-20251004.csv',
                       output_csv='data/satellite_master_list.csv'):
    """
    Create a master satellite list by cross-referencing satcat with active satellites
    """
    print("\n=== Creating Master Satellite List ===")
    
    # Load both datasets
    try:
        satcat_df = pd.read_csv(satcat_csv)
        active_df = pd.read_csv(active_csv)
        
        print(f"✓ Loaded {len(satcat_df)} satellites from satcat")
        print(f"✓ Loaded {len(active_df)} active satellites")
        
        # Identify common key columns (likely NORAD_CAT_ID or similar)
        satcat_cols = satcat_df.columns.tolist()
        active_cols = active_df.columns.tolist()
        
        print(f"\nSatcat columns: {satcat_cols[:5]}...")
        print(f"Active columns: {active_cols[:5]}...")
        
        # Try to find common identifier column
        # Common identifiers: NORAD_CAT_ID, OBJECT_ID, INTLDES, etc.
        common_id_names = ['NORAD_CAT_ID', 'NORAD', 'CATALOG_NUMBER', 'SATNO', 'OBJECT_NUMBER']
        
        satcat_id_col = None
        active_id_col = None
        
        for col in common_id_names:
            if col in satcat_cols and satcat_id_col is None:
                satcat_id_col = col
            if col in active_cols and active_id_col is None:
                active_id_col = col
        
        # If exact match not found, look for partial matches
        if not satcat_id_col:
            for col in satcat_cols:
                if 'NORAD' in col.upper() or 'CAT' in col.upper():
                    satcat_id_col = col
                    break
        
        if not active_id_col:
            for col in active_cols:
                if 'NORAD' in col.upper() or 'CAT' in col.upper():
                    active_id_col = col
                    break
        
        print(f"\nUsing ID columns:")
        print(f"  Satcat: {satcat_id_col}")
        print(f"  Active: {active_id_col}")
        
        if not satcat_id_col or not active_id_col:
            print("✗ Could not identify common ID column")
            return False
        
        # Convert JCAT to integer (remove 'S' prefix)
        satcat_df[satcat_id_col] = satcat_df[satcat_id_col].str.replace('S', '').astype(int)
        print(f"✓ Converted {satcat_id_col} from 'S00001' to integer format")
        
        # Add STATUS column to satcat
        satcat_df['STATUS'] = 'INACTIVE'
        
        # Mark satellites as ACTIVE if they exist in active list
        active_ids = set(active_df[active_id_col].astype(int))
        satcat_df.loc[satcat_df[satcat_id_col].isin(active_ids), 'STATUS'] = 'ACTIVE'
        
        active_count = (satcat_df['STATUS'] == 'ACTIVE').sum()
        inactive_count = (satcat_df['STATUS'] == 'INACTIVE').sum()
        
        print(f"\n✓ Status summary:")
        print(f"  Active: {active_count}")
        print(f"  Inactive: {inactive_count}")
        print(f"  Total: {len(satcat_df)}")
        
        # Merge additional data from active satellites
        if satcat_id_col and active_id_col:
            # Merge on the ID columns
            master_df = satcat_df.merge(
                active_df, 
                left_on=satcat_id_col, 
                right_on=active_id_col, 
                how='left',
                suffixes=('_SATCAT', '_ACTIVE')
            )
            print(f"✓ Merged data from both sources")
        else:
            master_df = satcat_df
        
        # Add metadata
        master_df['LAST_UPDATED'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        master_df['DATA_SOURCE'] = 'planet4589.org + Celestrak'
        
        # Save master list
        master_df.to_csv(output_csv, index=False)
        print(f"\n✓ Master list saved to {output_csv}")
        print(f"  Total entries: {len(master_df)}")
        print(f"  Columns: {len(master_df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating master list: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution flow"""
    print("=" * 60)
    print("SATELLITE CATALOG SCRAPER")
    print("=" * 60)
    
    # Step 1: Fetch HTML
    html_content = fetch_satcat_html()
    if not html_content:
        return
    
    # Step 2: Parse table
    result = parse_satcat_table(html_content)
    if not result:
        return
    
    headers, rows = result
    
    # Step 3: Save to CSV
    if not save_to_csv(headers, rows):
        return
    
    # Step 4: Create master list
    print("\n" + "=" * 60)
    create_master_list()
    
    print("\n" + "=" * 60)
    print("✓ COMPLETE!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  1. data/satcat_master.csv - Raw satellite catalog")
    print("  2. data/satellite_master_list.csv - Master list with status")

if __name__ == "__main__":
    main()
