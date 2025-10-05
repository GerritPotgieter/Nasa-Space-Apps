# 500 Satellites Update - Technical Summary

## Overview

Expanded satellite tracking from 50 to 500 active satellites with optimized visualization for the massive scale increase.

## Changes Made

### 1. Data Collection Script (`scripts/fetch_tle_n2yo.py`)

**Updated to fetch 500 satellites from master list:**

- Changed limit from 50 → 500 satellites
- Source changed: `active-20251004.csv` → `satellite_master_list.csv`
- **Filter**: Only fetches satellites with `STATUS = 'ACTIVE'`
- Handles whitespace in CSV columns (strips keys and values)
- Increased CSV field size limit to 10MB
- Added `TLE_FETCHED` flag (YES/NO) to track success

**Key Features:**

```python
# Reads only ACTIVE satellites from master list
if row.get('STATUS') == 'ACTIVE':
    satellites.append(row)

# Handles JCAT column as NORAD_CAT_ID
norad_id = sat.get('NORAD_CAT_ID') or sat.get('JCAT')
```

**Output File:**

- `data/satellites_with_tle_n2yo.csv` - 500 satellites with TLE data
- Each row contains master list data + TLE_LINE1, TLE_LINE2, N2YO_SAT_NAME

### 2. Globe Visualization (`assets/html/tracker.html`)

**Optimized for 500 satellites:**

| Property       | Old (50 sats) | New (500 sats) | Reason                       |
| -------------- | ------------- | -------------- | ---------------------------- |
| Box dimensions | 20,000m       | 5,000m         | 4x smaller to reduce clutter |
| Box alpha      | 0.9           | 0.7            | More transparent             |
| Box outline    | Yes           | No             | Cleaner visual               |
| Point size     | 6px           | 3px            | Half size for density        |
| Point alpha    | 1.0           | 0.9            | Slightly transparent         |
| Label font     | 10px          | 9px            | Smaller text                 |
| Label distance | 15M km        | 10M km         | Closer zoom for labels       |

**Visual Impact:**

- Satellites appear as small orange dots instead of large boxes
- Less visual noise with 10x more satellites
- Labels only appear when zoomed in closer
- Maintains performance with 500 real-time tracked objects

## Data Pipeline

```
satellite_master_list.csv (65,880 total)
    ↓ Filter STATUS = 'ACTIVE'
    ↓ First 500 entries
    ↓
fetch_tle_n2yo.py (N2YO API)
    ↓ Add TLE_LINE1, TLE_LINE2
    ↓ 1 second delay per request
    ↓ ~8-10 minutes total
    ↓
satellites_with_tle_n2yo.csv (500 with TLE)
    ↓ Load into globe
    ↓ SGP4 propagation
    ↓ Real-time updates
    ↓
Cesium Globe (tracker.html)
    → 500 satellites visible
    → Click to track any satellite
    → ESC to stop tracking
```

## Performance Considerations

**Why 500 satellites works:**

1. **Smaller visual elements** - 5k box vs 20k box = 64x less volume
2. **Point primitives** - GPU-accelerated rendering
3. **Distance-based labels** - Only show when zoomed in
4. **Efficient SGP4** - satellite.js propagates in real-time
5. **Altitude compression** - Visual scaling keeps satellites visible

**Expected Performance:**

- Load time: ~2-3 seconds (CSV parsing)
- FPS: 60fps on modern hardware
- Memory: ~50MB for 500 satellites
- Update rate: 60 times/second (Cesium clock)

## Testing the Update

### 1. Wait for TLE fetch to complete

```bash
# Monitor terminal - shows progress [X/500]
# Takes ~8-10 minutes
```

### 2. Verify output file

```bash
# Check file was created
ls data/satellites_with_tle_n2yo.csv

# Should show ~500 rows with TLE data
```

### 3. Open tracker page

```
Open: assets/html/tracker.html in browser
Expected: 500 small orange dots on globe
```

### 4. Interact with satellites

- **Zoom in**: Labels appear
- **Click satellite**: Tracks and shows info
- **Press ESC**: Stop tracking

## Satellite Distribution

**From master list (12,801 ACTIVE total):**

- Taking first 500 active satellites
- Mix of orbit types:
  - LEO (Low Earth Orbit): Most satellites
  - MEO (Medium Earth Orbit): GPS, Glonass, Galileo
  - GEO (Geostationary): Communication satellites
  - HEO (High Elliptical): Molniya orbits

**Altitude Scaling Applied:**

- LEO (<2000km): 1:1 scale
- MEO (2000-10000km): 40% compression
- GEO (>10000km): 20% compression

This makes GEO satellites visible without zooming out too far.

## Next Steps

### Potential Enhancements:

1. **Color coding by orbit type**

   - Blue: LEO
   - Yellow: MEO
   - Red: GEO
   - Purple: HEO

2. **Satellite filtering**

   - Dropdown to filter by orbit type
   - Search by NORAD ID or name
   - Show/hide specific orbit ranges

3. **Orbit path visualization**

   - Draw orbital path for tracked satellite
   - Show ground track

4. **Performance mode**

   - Toggle between 500 (full) and 50 (lite) modes
   - Adjust visual quality based on FPS

5. **Expand to all 12,801 active satellites**
   - Requires additional N2YO API calls (25+ hours at 1s delay)
   - May need performance optimizations
   - Could use point-only rendering (no boxes)

## Files Modified

```
scripts/fetch_tle_n2yo.py
  - Changed limit to 500
  - Source: satellite_master_list.csv
  - Filter: STATUS = 'ACTIVE'
  - Added TLE_FETCHED flag

assets/html/tracker.html
  - Box: 20k → 5k dimensions
  - Box: outline removed
  - Point: 6px → 3px
  - Label: distance reduced
  - Alpha values adjusted
```

## Status

✅ Script updated and running
✅ Globe visualization optimized
⏳ TLE fetch in progress (~8 minutes remaining)
⏳ Testing pending after data collection

**Estimated completion:** 8-10 minutes from script start
**Current progress:** Check terminal for [X/500] status
