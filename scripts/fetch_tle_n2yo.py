"""
Fetch TLE data for first 50 satellites from active-20251004.csv
using the N2YO API and combine with their orbital data into a merged CSV.
"""

import csv
import time
import requests
import os
from pathlib import Path
from datetime import datetime

# Increase CSV field size limit for large fields
csv.field_size_limit(10000000)  # 10MB limit

class N2YOError(Exception):
    pass

def load_env():
    """Load environment variables from .env file"""
    # Check parent directory first
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print(f"⚠ .env file not found at {env_path}")

def fetch_tle_n2yo(norad_id, api_key):
    """
    Fetch TLE data from N2YO API for a single NORAD ID.
    
    Returns:
        dict with TLE data or None if not found
    """
    url = f"https://api.n2yo.com/rest/v1/satellite/tle/{norad_id}"
    params = {'apiKey': api_key}
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        
        if not resp.ok:
            print(f"  ⚠ Failed to fetch TLE for {norad_id}: HTTP {resp.status_code}")
            return None
        
        data = resp.json()
        
        # N2YO returns data in this format:
        # {
        #   "info": {
        #     "satid": 25544,
        #     "satname": "SPACE STATION",
        #     ...
        #   },
        #   "tle": "1 25544U...\n2 25544..."
        # }
        
        if 'tle' not in data:
            print(f"  ⚠ No TLE data in response for {norad_id}")
            return None
        
        tle_string = data['tle']
        tle_lines = tle_string.strip().split('\n')
        
        if len(tle_lines) < 2:
            print(f"  ⚠ Invalid TLE format for {norad_id}")
            return None
        
        info = data.get('info', {})
        sat_name = info.get('satname', 'Unknown')
        
        print(f"  ✓ Fetched TLE for {norad_id}: {sat_name}")
        
        return {
            'NORAD_CAT_ID': str(norad_id),
            'OBJECT_NAME': sat_name,
            'TLE_LINE1': tle_lines[0].strip(),
            'TLE_LINE2': tle_lines[1].strip() if len(tle_lines) > 1 else '',
            'SAT_ID': info.get('satid', ''),
            'SAT_NAME': sat_name
        }
    
    except requests.exceptions.RequestException as e:
        print(f"  ⚠ Network error fetching TLE for {norad_id}: {e}")
        return None
    except Exception as e:
        print(f"  ⚠ Error parsing TLE for {norad_id}: {e}")
        return None

def read_active_satellites(csv_path, limit=500):
    """
    Read first N ACTIVE satellites from master list CSV.
    
    Returns:
        list of dicts with satellite data
    """
    satellites = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Strip whitespace from keys and values, handle None
            cleaned_row = {}
            for k, v in row.items():
                if k is not None:
                    key = k.strip()
                    value = v.strip() if v else ''
                    cleaned_row[key] = value
            
            # Only include satellites with STATUS = 'ACTIVE'
            if cleaned_row.get('STATUS') == 'ACTIVE':
                satellites.append(cleaned_row)
                if len(satellites) >= limit:
                    break
    
    print(f"✓ Loaded {len(satellites)} ACTIVE satellites from {csv_path}")
    return satellites

def merge_data(active_sat, tle_data):
    """
    Merge active satellite data with TLE data from N2YO.
    
    Returns:
        dict with combined data
    """
    merged = active_sat.copy()
    
    if tle_data:
        # Add TLE lines from N2YO
        merged['TLE_LINE1'] = tle_data.get('TLE_LINE1', '')
        merged['TLE_LINE2'] = tle_data.get('TLE_LINE2', '')
        merged['N2YO_SAT_NAME'] = tle_data.get('SAT_NAME', '')
        merged['TLE_FETCHED'] = 'YES'
    else:
        # Add empty TLE fields if fetch failed
        merged['TLE_LINE1'] = ''
        merged['TLE_LINE2'] = ''
        merged['N2YO_SAT_NAME'] = ''
        merged['TLE_FETCHED'] = 'NO'
    
    return merged

def save_merged_csv(data, output_path):
    """
    Save merged data to CSV.
    """
    if not data:
        print("⚠ No data to save")
        return
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✓ Saved merged data to {output_path}")

def generate_postgres_schema(sample_data, table_name='satellites_n2yo'):
    """
    Generate PostgreSQL CREATE TABLE statement based on sample data.
    """
    schema = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    schema += "    id SERIAL PRIMARY KEY,\n"
    
    for key in sample_data.keys():
        # Determine column type based on field name
        col_name = key.lower()
        
        if 'norad' in col_name or 'id' in col_name or 'cat' in col_name:
            col_type = "VARCHAR(50)"
        elif 'epoch' in col_name or 'date' in col_name:
            col_type = "TIMESTAMP"
        elif 'name' in col_name or 'type' in col_name or 'class' in col_name:
            col_type = "VARCHAR(255)"
        elif 'line' in col_name:
            col_type = "TEXT"
        elif any(x in col_name for x in ['motion', 'eccentric', 'inclin', 'anomaly', 'node', 'pericenter', 'bstar']):
            col_type = "DOUBLE PRECISION"
        else:
            col_type = "VARCHAR(255)"
        
        schema += f"    {col_name} {col_type},\n"
    
    schema += "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
    schema += ");\n"
    
    # Add index on NORAD_CAT_ID for faster lookups
    schema += f"\nCREATE INDEX IF NOT EXISTS idx_{table_name}_norad ON {table_name}(norad_cat_id);\n"
    
    return schema

def main():
    print("=" * 60)
    print("Satellite TLE Batch Fetcher (N2YO API)")
    print("=" * 60)
    
    # Load credentials
    load_env()
    api_key = os.getenv('NY2_API_KEY')
    
    if not api_key:
        print("❌ Error: NY2_API_KEY must be set in .env file")
        return
    
    print(f"✓ Loaded N2YO API key: {api_key[:8]}...")
    
    # Configuration
    input_csv = Path(__file__).parent.parent / 'data' / 'satellite_master_list.csv'
    output_csv = Path(__file__).parent.parent / 'data' / 'satellites_with_tle_n2yo.csv'
    schema_file = Path(__file__).parent.parent / 'data' / 'postgres_schema_n2yo.sql'
    limit = 500
    
    if not input_csv.exists():
        print(f"❌ Error: Input file not found: {input_csv}")
        return
    
    # Step 1: Read active satellites
    print(f"\n[1/4] Reading first {limit} satellites...")
    satellites = read_active_satellites(input_csv, limit=limit)
    
    # Step 2: Fetch TLE data for each satellite
    print(f"\n[2/4] Fetching TLE data from N2YO for {len(satellites)} satellites...")
    print("(This may take a minute - N2YO rate limits apply)\n")
    
    merged_data = []
    success_count = 0
    fail_count = 0
    
    for i, sat in enumerate(satellites, 1):
        # Try to get NORAD ID from different possible column names
        norad_id = sat.get('NORAD_CAT_ID') or sat.get('JCAT') or sat.get('norad_cat_id')
        
        if not norad_id:
            print(f"[{i}/{len(satellites)}] ⚠ No NORAD ID found, skipping...")
            merged = merge_data(sat, None)
            merged_data.append(merged)
            fail_count += 1
            continue
        
        print(f"[{i}/{len(satellites)}] Processing {norad_id}...")
        
        tle_data = fetch_tle_n2yo(norad_id, api_key)
        merged = merge_data(sat, tle_data)
        merged_data.append(merged)
        
        if tle_data:
            success_count += 1
        else:
            fail_count += 1
        
        # Be nice to the API - add delay between requests
        if i < len(satellites):
            time.sleep(1)  # 1 second delay for N2YO
    
    # Step 3: Save merged CSV
    print(f"\n[3/4] Saving merged data...")
    save_merged_csv(merged_data, output_csv)
    
    # Step 4: Generate PostgreSQL schema
    print(f"\n[4/4] Generating PostgreSQL schema...")
    if merged_data:
        schema = generate_postgres_schema(merged_data[0])
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(schema)
        print(f"✓ Saved PostgreSQL schema to {schema_file}")
        print("\nSchema preview:")
        print("-" * 60)
        print(schema[:500] + "..." if len(schema) > 500 else schema)
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ Batch processing complete!")
    print("=" * 60)
    print(f"\nStatistics:")
    print(f"  - Total processed: {len(satellites)}")
    print(f"  - Successful: {success_count}")
    print(f"  - Failed: {fail_count}")
    print(f"\nOutput files:")
    print(f"  - CSV data: {output_csv}")
    print(f"  - SQL schema: {schema_file}")
    print(f"\nNext steps:")
    print(f"  1. Create PostgreSQL database")
    print(f"  2. Run: psql -d your_db -f {schema_file}")
    print(f"  3. Import CSV: \\copy satellites_n2yo FROM '{output_csv.absolute()}' CSV HEADER")

if __name__ == "__main__":
    main()
