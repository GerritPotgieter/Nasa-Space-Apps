"""
Fetch TLE data for first 50 satellites from active-20251004.csv
and combine with their orbital data into a merged CSV for PostgreSQL import.
"""

import csv
import time
import requests
import os
from pathlib import Path
from datetime import datetime

class SpaceTrackError(Exception):
    pass

def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def create_spacetrack_session(username, password):
    """
    Create an authenticated Space-Track session.
    
    Returns:
        requests.Session object with authentication cookie
    """
    base = "https://www.space-track.org"
    login_url = base + "/ajaxauth/login"
    
    session = requests.Session()
    
    login_data = {
        'identity': username,
        'password': password
    }
    
    resp = session.post(login_url, data=login_data, timeout=10)
    if not resp.ok:
        raise SpaceTrackError(f"Login failed - HTTP {resp.status_code}: {resp.text}")
    
    print("✓ Authenticated with Space-Track")
    return session

def fetch_tle_for_norad(session, norad_id):
    """
    Fetch the latest TLE data for a single NORAD ID.
    
    Returns:
        dict with TLE data or None if not found
    """
    base = "https://www.space-track.org"
    query_url = base + f"/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{norad_id}/orderby/EPOCH%20desc/limit/1/format/csv"
    
    try:
        resp = session.get(query_url, timeout=10)
        if not resp.ok:
            print(f"  ⚠ Failed to fetch TLE for {norad_id}: HTTP {resp.status_code}")
            return None
        
        # Parse CSV response
        lines = resp.text.strip().split('\n')
        if len(lines) < 2:
            print(f"  ⚠ No TLE data found for {norad_id}")
            return None
        
        # Parse header and data
        reader = csv.DictReader(lines)
        tle_data = next(reader, None)
        
        if tle_data:
            print(f"  ✓ Fetched TLE for {norad_id}: {tle_data.get('OBJECT_NAME', 'Unknown')}")
        
        return tle_data
    
    except Exception as e:
        print(f"  ⚠ Error fetching TLE for {norad_id}: {e}")
        return None

def read_active_satellites(csv_path, limit=50):
    """
    Read first N satellites from active CSV.
    
    Returns:
        list of dicts with satellite data
    """
    satellites = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            satellites.append(row)
    
    print(f"✓ Loaded {len(satellites)} satellites from {csv_path}")
    return satellites

def merge_data(active_sat, tle_data):
    """
    Merge active satellite data with TLE data.
    
    Returns:
        dict with combined data
    """
    merged = active_sat.copy()
    
    if tle_data:
        # Add TLE-specific fields with prefix to avoid collision
        merged['TLE_LINE1'] = tle_data.get('TLE_LINE1', '')
        merged['TLE_LINE2'] = tle_data.get('TLE_LINE2', '')
        merged['TLE_EPOCH'] = tle_data.get('EPOCH', '')
        merged['TLE_MEAN_MOTION'] = tle_data.get('MEAN_MOTION', '')
        merged['TLE_ECCENTRICITY'] = tle_data.get('ECCENTRICITY', '')
        merged['TLE_INCLINATION'] = tle_data.get('INCLINATION', '')
        merged['TLE_RA_OF_ASC_NODE'] = tle_data.get('RA_OF_ASC_NODE', '')
        merged['TLE_ARG_OF_PERICENTER'] = tle_data.get('ARG_OF_PERICENTER', '')
        merged['TLE_MEAN_ANOMALY'] = tle_data.get('MEAN_ANOMALY', '')
    else:
        # Add empty TLE fields if fetch failed
        merged['TLE_LINE1'] = ''
        merged['TLE_LINE2'] = ''
        merged['TLE_EPOCH'] = ''
        merged['TLE_MEAN_MOTION'] = ''
        merged['TLE_ECCENTRICITY'] = ''
        merged['TLE_INCLINATION'] = ''
        merged['TLE_RA_OF_ASC_NODE'] = ''
        merged['TLE_ARG_OF_PERICENTER'] = ''
        merged['TLE_MEAN_ANOMALY'] = ''
    
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

def generate_postgres_schema(sample_data, table_name='satellites'):
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
    print("Satellite TLE Batch Fetcher")
    print("=" * 60)
    
    # Load credentials
    load_env()
    username = os.getenv('ST_USERNAME')
    password = os.getenv('ST_PASSWORD')
    
    if not username or not password:
        print("❌ Error: ST_USERNAME and ST_PASSWORD must be set in .env file")
        return
    
    # Configuration
    input_csv = Path('data/active-20251004.csv')
    output_csv = Path('data/satellites_with_tle.csv')
    schema_file = Path('data/postgres_schema.sql')
    limit = 50
    
    if not input_csv.exists():
        print(f"❌ Error: Input file not found: {input_csv}")
        return
    
    # Step 1: Read active satellites
    print(f"\n[1/5] Reading first {limit} satellites...")
    satellites = read_active_satellites(input_csv, limit=limit)
    
    # Step 2: Authenticate with Space-Track
    print("\n[2/5] Authenticating with Space-Track...")
    session = create_spacetrack_session(username, password)
    
    # Step 3: Fetch TLE data for each satellite
    print(f"\n[3/5] Fetching TLE data for {len(satellites)} satellites...")
    print("(This may take a minute - Space-Track rate limits apply)\n")
    
    merged_data = []
    for i, sat in enumerate(satellites, 1):
        norad_id = sat.get('NORAD_CAT_ID')
        print(f"[{i}/{len(satellites)}] Processing {norad_id}...")
        
        tle_data = fetch_tle_for_norad(session, norad_id)
        merged = merge_data(sat, tle_data)
        merged_data.append(merged)
        
        # Be nice to the API - add delay between requests
        if i < len(satellites):
            time.sleep(0.5)  # 500ms delay
    
    # Step 4: Save merged CSV
    print(f"\n[4/5] Saving merged data...")
    save_merged_csv(merged_data, output_csv)
    
    # Step 5: Generate PostgreSQL schema
    print(f"\n[5/5] Generating PostgreSQL schema...")
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
    print(f"\nOutput files:")
    print(f"  - CSV data: {output_csv}")
    print(f"  - SQL schema: {schema_file}")
    print(f"\nNext steps:")
    print(f"  1. Create PostgreSQL database")
    print(f"  2. Run: psql -d your_db -f {schema_file}")
    print(f"  3. Import CSV: \\copy satellites FROM '{output_csv.absolute()}' CSV HEADER")

if __name__ == "__main__":
    main()
