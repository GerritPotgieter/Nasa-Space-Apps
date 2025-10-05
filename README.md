# THE ORB - Satellite Operations Platform

**Precision Beyond Orbit** - A comprehensive satellite tracking, registry, insurance, and compliance management system.

## Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** (optional, for development tools) - [Download Node.js](https://nodejs.org/)

## Quick Start

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

The `requirements.txt` includes:
- Flask (web server)
- requests (HTTP library)
- python-dotenv (environment management)
- Other data processing libraries

### 2. Install Node.js Dependencies (Optional)

If you're using any Node.js build tools or development dependencies:

```powershell
npm install
```

### 3. Start the HTTP Server

The application uses Python's built-in HTTP server. Run from the project root:

```powershell
python -m http.server 8080
```

**Default address:** `http://localhost:8080`

### 4. Access the Application

Open your browser and navigate to:

- **Dashboard**: http://localhost:8080/assets/html/dashboard.html
- **Satellite Tracker**: http://localhost:8080/assets/html/tracker_v2.html
- **Registry**: http://localhost:8080/assets/html/registry.html
- **Insurance**: http://localhost:8080/assets/html/insurance_new.html
- **Compliance**: http://localhost:8080/assets/html/compliance.html

## Project Structure

```
Nasa Space Apps/
├── api.py                      # Main HTTP server
├── requirements.txt            # Python dependencies
├── assets/
│   ├── html/                   # Application pages
│   │   ├── dashboard.html      # Main landing page
│   │   ├── tracker_v2.html     # 3D satellite tracking
│   │   ├── registry.html       # 65,880 satellite database
│   │   ├── insurance_new.html  # Fleet insurance management
│   │   └── compliance.html     # Big Five treaty tracker
│   └── js/                     # JavaScript modules
│       ├── globe.js
│       └── satellites.js
├── data/                       # Satellite data files
│   ├── active-20251004.csv
│   ├── satcat_master.csv
│   └── satellites_with_tle_n2yo.csv
├── scripts/                    # Utility scripts
└── readmes/                    # Documentation
```

## Features

### 🌍 3D Satellite Tracker (tracker_v2.html)
- Real-time satellite visualization with Cesium.js
- Live orbital paths and ground tracks
- Search and filter 65,880+ satellites

### 📊 Satellite Registry (registry.html)
- Complete SATCAT database
- Advanced filtering (owner, orbit type, status)
- Pagination for large datasets

### 🛡️ Fleet Insurance (insurance_new.html)
- Coverage management for satellite fleets
- Risk assessment and policy tracking
- Tier-based access control

### ⚖️ Compliance Tracker (compliance.html)
- Big Five treaty compliance monitoring
- OST, Rescue, Liability, Registration, ITU Radio
- Jurisdiction analysis

## Development

### Running Scripts

Update satellite data:
```powershell
python scripts/update_active_satellites.py
```

Fetch TLE data:
```powershell
python scripts/fetch_tle_n2yo.py
```

### API Endpoints

The `api.py` server provides:
- Satellite data queries
- TLE updates
- Registry search/filter

## Troubleshooting

**Port 8080 already in use:**
```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Python not found:**
- Ensure Python is added to PATH during installation
- Restart terminal after installing Python

**Module not found errors:**
- Run `pip install -r requirements.txt` again
- Check Python version: `python --version`

## Design System

**ORB Brand Guidelines:**
- **Typography**: Playfair Display (headers), Inter (body)
- **Colors**: Deep Charcoal (#121212), Off-White (#eaeaea), Accent Orange (#e85d04)
- **Effects**: Glassmorphism with blur(20px)

## License

NASA Space Apps Challenge 2024 Project

## Support

For issues or questions, check the `/readmes` directory for detailed documentation on specific features.
