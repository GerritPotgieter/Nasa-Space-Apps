# 🛰️ THE ORB

> **Precision Beyond Orbit** - Unified satellite tracking, registry, and management platform

A comprehensive web-based system for real-time satellite visualization, data management, insurance tracking, and regulatory compliance monitoring.

![Satellite Tracker](https://img.shields.io/badge/Satellites-65%2C880-orange)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## ✨ Features

- **🌍 3D Satellite Tracker** - Real-time visualization of 65,880+ satellites using Cesium.js
- **📋 Satellite Registry** - Comprehensive database with 60+ data fields per satellite
- **🛡️ Insurance Management** - Track policies, coverage, and claims
- **⚖️ Compliance Hub** - Monitor treaty adherence and regulatory requirements
- **🎯 Advanced Filtering** - Filter by status, orbit type, country, organization, and more

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge)

### Installation & Running

1. **Clone the repository**

   ```bash
   git clone https://github.com/GerritPotgieter/Nasa-Space-Apps.git
   cd Nasa-Space-Apps
   ```

2. **Start the local server**

   ```bash
   python -m http.server 8080
   ```

3. **Open in browser**
   ```
   http://localhost:8080/assets/html/dashboard.html
   ```

That's it! 🎉

---

## 📂 Project Structure

```
Nasa-Space-Apps/
├── assets/
│   ├── html/           # All HTML pages
│   ├── js/             # JavaScript modules
│   └── css/            # Shared stylesheets
├── data/               # Satellite datasets (CSV)
├── scripts/            # Data fetching scripts
└── README.md
```

---

## 🗺️ Navigation

| Page          | URL                            | Description                             |
| ------------- | ------------------------------ | --------------------------------------- |
| **Dashboard** | `/assets/html/dashboard.html`  | Platform overview with feature previews |
| **Tracker**   | `/assets/html/tracker_v2.html` | 3D real-time satellite visualization    |
| **Registry**  | `/assets/html/registry.html`   | Searchable satellite database           |
| **Tools**     | `/assets/html/tools.html`      | Insurance & compliance tools hub        |

---

## 🛠️ Technologies

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **3D Visualization**: Cesium.js 1.118
- **Orbital Mechanics**: Satellite.js 5.0
- **Charts**: Chart.js 3.9
- **Data**: TLE orbital elements, satellite registry CSVs

---

## 📊 Data Sources

- Satellite catalog data from space-track.org
- TLE (Two-Line Element) orbital data
- Organization and ownership information
- Compliance and treaty databases

---

## 🤝 Contributing

Contributions welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🌟 Acknowledgments

Built for NASA Space Apps Challenge 2024

- Team: Space Operations Excellence
- Challenge: Satellite Operations Management

---

**Made with 🚀 by GerritPotgieter**

- Tier-based access control

### ⚖️ Compliance Tracker (compliance.html)

- Big Five treaty compliance monitoring
- OST, Rescue, Liability, Registration, ITU Radio
- Jurisdiction analysis

## License

NASA Space Apps Challenge 2024 Project
