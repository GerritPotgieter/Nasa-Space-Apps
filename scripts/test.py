import requests
import os
from pathlib import Path

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

def fetch_latest_tle_csv(norad_id, username, password):
    """
    Fetch the latest TLE data in CSV format for satellites around a NORAD catalog ID.
    Uses Space-Track.org session-based authentication.

    Returns:
        CSV text response
    """
    base = "https://www.space-track.org"
    login_url = base + "/ajaxauth/login"
    query_url = base + f"/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{norad_id}/orderby/EPOCH%20desc/limit/1/format/csv"
    
    # Create a session to persist cookies
    session = requests.Session()
    
    # Login to get authentication cookie
    login_data = {
        'identity': username,
        'password': password
    }
    
    resp = session.post(login_url, data=login_data, timeout=10)
    if not resp.ok:
        raise SpaceTrackError(f"Login failed - HTTP {resp.status_code}: {resp.text}")
    
    # Now query with the authenticated session
    resp = session.get(query_url, timeout=10)
    if not resp.ok:
        raise SpaceTrackError(f"Query failed - HTTP {resp.status_code}: {resp.text}")
    
    return resp.text

def main():
    # Load credentials from .env file
    load_env()
    username = os.getenv('ST_USERNAME')
    password = os.getenv('ST_PASSWORD')
    
    if not username or not password:
        print("Error: ST_USERNAME and ST_PASSWORD must be set in .env file")
        return
    
    norad_id = input("Enter NORAD catalog ID (default: 900): ").strip() or "900"
    
    try:
        csv_data = fetch_latest_tle_csv(norad_id, username, password)
        print("CSV Response:")
        print(csv_data)
    except SpaceTrackError as e:
        print("Error fetching TLE:", e)

if __name__ == "__main__":
    main()
