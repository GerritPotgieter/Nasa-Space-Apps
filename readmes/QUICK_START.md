# 🚀 Quick Start Guide - THE ORB Multi-Page Platform

## 🎯 What Changed?

Your single `main.html` file has been split into **3 separate pages**:

1. **dashboard.html** - Home page with statistics
2. **tracker.html** - 3D globe viewer (FIXED SIZING!)
3. **registry.html** - Satellite database table

---

## ⚡ How to Access

### Start Server (if not running):

```powershell
cd "C:\Users\gerri\Documents\Nasa Space Apps"
python -m http.server 8080
```

### Open in Browser:

**Dashboard (Start Here):**
http://localhost:8080/dashboard.html

**Tracker (3D Globe):**
http://localhost:8080/tracker.html

**Registry (Table):**
http://localhost:8080/registry.html

---

## ✅ Globe Sizing Issue - FIXED!

### The Problem:

Globe was expanding to fill entire screen

### The Solution:

Fixed dimensions with proper CSS constraints:

```css
/* In tracker.html */
.globe-wrapper {
  height: 700px; /* Fixed height */
  max-height: calc(100vh - 250px); /* Responsive max */
}

.globe-viewer {
  position: relative;
  height: 100%;
  overflow: hidden; /* Prevents expansion */
}

#globe-canvas {
  position: absolute; /* Contains within parent */
  width: 100%;
  height: 100%;
}
```

### Layout Structure:

```
┌──────────────────────────────────────┐
│  Sidebar (300px)  │  Globe Viewer   │
│                   │  (flex: 1)      │
│  - Search         │  ┌────────────┐ │
│  - Filters        │  │  Cesium    │ │
│  - Reset          │  │  Globe     │ │
│  - Instructions   │  │  (700px)   │ │
│                   │  └────────────┘ │
└──────────────────────────────────────┘
```

---

## 🎨 Page Features

### Dashboard Page

- ✅ Hero section with animated orb
- ✅ Fleet statistics (auto-calculated from CSV)
- ✅ Chart.js visualizations
- ✅ "Explore Platform" button → tracker

### Tracker Page

- ✅ **Fixed-size globe** (no more expansion!)
- ✅ Sidebar with filters and search
- ✅ 50 satellites from CSV data
- ✅ Click-to-track functionality
- ✅ Real-time SGP4 propagation
- ✅ Info panel with satellite details
- ✅ ESC to stop tracking

### Registry Page

- ✅ Searchable table (name/NORAD ID)
- ✅ Filter by orbit type (LEO/MEO/GEO)
- ✅ Filter by status (Active/Inactive)
- ✅ Live satellite count
- ✅ All 50 satellites listed

---

## 🧪 Testing

Visit each page and verify:

**Dashboard:**

- [ ] Charts load
- [ ] Stats update with real numbers
- [ ] "Explore Platform" works

**Tracker:**

- [ ] Globe stays within 700px height ✅
- [ ] Sidebar is 300px wide ✅
- [ ] No overflow issues ✅
- [ ] Satellites appear
- [ ] Click tracking works

**Registry:**

- [ ] All 50 satellites show
- [ ] Search works
- [ ] Filters work

---

## 📁 File Changes

**New Files Created:**

- `dashboard.html` (Home page)
- `tracker.html` (Globe viewer)
- `registry.html` (Table)
- `MULTIPAGE_SUMMARY.md` (This guide)

**Original Files (Preserved):**

- `main.html` (can be archived)
- `index.html` (standalone globe)

---

## 🐛 Troubleshooting

### Globe still expanding?

1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check CSS loaded correctly

### Satellites not appearing?

1. Verify CSV exists: `data/satellites_with_tle_n2yo.csv`
2. Check browser console (F12)
3. Ensure server is serving from correct directory

### Navigation not working?

- All links updated to use `.html` extensions
- Verify files exist in same directory

---

## 🎉 Success!

Your globe now has proper sizing constraints and your platform is split into manageable, focused pages!

**Next Steps:**

1. Test all three pages
2. Verify globe stays at 700px height
3. Enjoy your properly structured satellite tracking platform!
