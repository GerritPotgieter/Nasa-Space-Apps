# 🐛 Globe Not Loading - Troubleshooting Guide

## ✅ Fixes Applied

### 1. Updated Cesium Configuration

Changed from `terrainProvider: undefined` to `imageryProvider: false` to match working index.html

### 2. Added Country Borders

Added GeoJSON loading for country outlines with proper styling

### 3. Added Loading Indicator

Shows "Loading Globe..." until Cesium initializes

### 4. Added Console Logging

Debug messages will appear in browser console (F12)

---

## 🔍 How to Debug

1. **Open Browser Console** (F12)
2. **Navigate to:** http://localhost:8080/tracker.html
3. **Check for messages:**
   - "Initializing Cesium Globe..."
   - "Container: [object HTMLDivElement]"
   - "Cesium Viewer created successfully"
   - "Country borders loaded"

---

## 🚨 Common Issues & Solutions

### Issue: Black screen / No globe visible

**Cause:** CSS positioning issue or Cesium not initializing

**Solution:**

- Check browser console for errors
- Verify Cesium.js CDN is loading (check Network tab)
- Clear browser cache (Ctrl+Shift+Delete)

### Issue: "Loading Globe..." never disappears

**Cause:** JavaScript error during initialization

**Solution:**

- Check console for error messages
- Verify `globe-canvas` div exists
- Check if Cesium library loaded

### Issue: Globe loads but satellites don't appear

**Cause:** CSV file not loading or parsing error

**Solution:**

- Check console for "Error loading satellites"
- Verify `data/satellites_with_tle_n2yo.csv` exists
- Check Network tab for 404 errors

---

## 📊 Expected Console Output

```
Initializing Cesium Globe...
Container: <div id="globe-canvas">...</div>
Cesium Viewer created successfully
Country borders loaded
Loaded 50 satellites
```

---

## 🔧 Manual Test Steps

1. Start server: `python -m http.server 8080`
2. Open: http://localhost:8080/tracker.html
3. Wait 2-3 seconds for globe to load
4. You should see:
   - Dark grey globe
   - White country outlines
   - Orange satellite boxes
5. Try clicking a satellite
6. Try pressing ESC to stop tracking

---

## 🎯 Key Changes from Original

**Before:**

```javascript
globeViewer = new Cesium.Viewer(container, {
  terrainProvider: undefined, // ❌ Can cause issues
  baseLayerPicker: false,
  // ...
});
```

**After:**

```javascript
globeViewer = new Cesium.Viewer(container, {
  imageryProvider: false, // ✅ Matches working index.html
  baseLayerPicker: false,
  // ...
});

// Added dark ocean
globeViewer.scene.globe.baseColor = Cesium.Color.fromCssColorString("#2b2b2b");

// Added country borders
Cesium.GeoJsonDataSource.load("...countries.geo.json");
```

---

## 🌐 Check These URLs

- **Dashboard:** http://localhost:8080/dashboard.html (should work)
- **Tracker:** http://localhost:8080/tracker.html (globe now loading)
- **Registry:** http://localhost:8080/registry.html (should work)
- **Original:** http://localhost:8080/index.html (working reference)

---

## 🔄 If Still Not Working

1. **Compare with working version:**

   - Open http://localhost:8080/index.html (this works)
   - Open http://localhost:8080/tracker.html (check if matches)

2. **Check file paths:**

   ```
   Nasa Space Apps/
   ├── tracker.html          ← New file
   ├── index.html            ← Working reference
   └── data/
       └── satellites_with_tle_n2yo.csv
   ```

3. **Verify Cesium CDN:**

   - Open Network tab (F12)
   - Look for: `Cesium.js` (should be 200 OK)
   - Look for: `widgets.css` (should be 200 OK)

4. **Check CSS:**
   - Globe container should have: `height: 700px`
   - Canvas should have: `position: absolute`
   - Wrapper should have: `overflow: hidden`

---

## 💡 Quick Fix Checklist

- [ ] Server running on port 8080
- [ ] Cesium.js CDN loading (check Network tab)
- [ ] No JavaScript errors in console
- [ ] CSV file exists at `data/satellites_with_tle_n2yo.csv`
- [ ] Browser cache cleared
- [ ] Hard refresh (Ctrl+F5)

---

## 📞 Next Steps

If globe still doesn't load:

1. Check browser console output
2. Compare Network requests with working index.html
3. Verify CSS is applying correctly (inspect element)
4. Test in different browser (Chrome/Firefox/Edge)

---

**Status:** Globe loading fix applied with debug logging enabled
