# Real-Time Satellite Tracker 🛰️🌍

A 3D visualization of real satellites using TLE (Two-Line Element) data and accurate orbital mechanics.

## Features

✅ **Real satellite data** from Space-Track / N2YO APIs  
✅ **Accurate orbital mechanics** using satellite.js library  
✅ **50 real satellites** from your CSV dataset  
✅ **Real-time propagation** using TLE data  
✅ **Interactive tracking** - click any satellite to follow it  
✅ **Detailed info panels** with orbital parameters  
✅ **Orange satellite markers** for easy visibility

## How It Works

### Data Pipeline

1. `fetch_tle_n2yo.py` - Fetches TLE data from N2YO API for 50 satellites
2. `data/satellites_with_tle_n2yo.csv` - Stores satellite metadata + TLE lines
3. `index.html` - Loads CSV, parses TLE, and propagates orbits using satellite.js

### Orbital Propagation

- Uses **SGP4** (Simplified General Perturbations) algorithm via satellite.js
- Converts TLE → ECI coordinates → Geodetic (lat/lon/alt)
- Updates positions in real-time based on current system time
- Accounts for Earth's rotation (GMST)

## Usage

### Start the Server

```powershell
python -m http.server 8080
```

### Open in Browser

Navigate to: http://localhost:8080

### Interact with Satellites

- **Click** any orange satellite to see details and track it
- **ESC** to stop tracking
- Satellite labels appear when zoomed in

## Satellite Data

Each satellite displays:

- **Name** (from N2YO or object name)
- **NORAD ID** (unique identifier)
- **Altitude** (calculated from TLE)
- **Orbital Period** (derived from mean motion)
- **Inclination** (orbital tilt)
- **Eccentricity** (orbit shape)
- **Epoch** (TLE timestamp)

## Files

- `index.html` - Main visualization (Cesium + satellite.js)
- `satellites.js` - Satellite data manager (standalone utility)
- `fetch_tle_n2yo.py` - Data fetcher from N2YO API
- `data/satellites_with_tle_n2yo.csv` - 50 satellites with TLE data

## Technologies

- **Cesium.js** - 3D globe rendering
- **satellite.js** - SGP4 orbital propagation
- **N2YO API** - TLE data source
- **Python** - Data fetching and CSV generation

## Next Steps

To add more satellites:

```powershell
# Edit fetch_tle_n2yo.py and change limit parameter
python fetch_tle_n2yo.py
```

To update TLE data (recommended daily):

```powershell
python fetch_tle_n2yo.py
```

## Accuracy

⚠️ TLE data degrades over time. For best accuracy:

- Update TLE data daily
- Satellites are most accurate within 24-48 hours of epoch
- Propagation uses simplified atmospheric models (suitable for visualization)

## Resources

- [Satellite.js Documentation](https://github.com/shashwatak/satellite-js)
- [TLE Format Explanation](https://en.wikipedia.org/wiki/Two-line_element_set)
- [SGP4 Theory](https://celestrak.org/NORAD/documentation/spacetrk.pdf)
- [N2YO API](https://www.n2yo.com/api/)

---

**Built for NASA Space Apps Challenge 2025** 🚀
