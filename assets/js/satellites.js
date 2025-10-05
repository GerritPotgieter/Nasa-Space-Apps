// Satellite data loader and orbital propagator using satellite.js
// Load and parse CSV data, then use TLE to calculate accurate positions

class SatelliteManager {
    constructor() {
        this.satellites = [];
        this.satelliteRecords = [];
    }

    // Parse CSV text into array of objects
    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        const records = [];

        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            const record = {};

            headers.forEach((header, index) => {
                record[header.trim()] = values[index] ? values[index].trim() : '';
            });

            // Only include satellites with valid TLE data
            if (record.TLE_LINE1 && record.TLE_LINE2) {
                records.push(record);
            }
        }

        return records;
    }

    // Load satellite data from CSV file
    async loadFromCSV(csvPath) {
        try {
            const response = await fetch(csvPath);
            const csvText = await response.text();
            this.satelliteRecords = this.parseCSV(csvText);
            console.log(`✓ Loaded ${this.satelliteRecords.length} satellites with TLE data`);
            return this.satelliteRecords;
        } catch (error) {
            console.error('Error loading CSV:', error);
            throw error;
        }
    }

    // Initialize satellite.js propagators for each satellite
    initializeSatellites() {
        this.satellites = this.satelliteRecords.map(record => {
            // Initialize TLE data for satellite.js
            const tleLine1 = record.TLE_LINE1;
            const tleLine2 = record.TLE_LINE2;

            try {
                // Create satellite record from TLE
                const satrec = satellite.twoline2satrec(tleLine1, tleLine2);

                return {
                    satrec: satrec,
                    name: record.N2YO_SAT_NAME || record.OBJECT_NAME || `SAT-${record.NORAD_CAT_ID}`,
                    noradId: record.NORAD_CAT_ID,
                    objectId: record.OBJECT_ID,
                    epoch: record.EPOCH,
                    inclination: parseFloat(record.INCLINATION) || 0,
                    eccentricity: parseFloat(record.ECCENTRICITY) || 0,
                    meanMotion: parseFloat(record.MEAN_MOTION) || 0,
                    record: record
                };
            } catch (error) {
                console.warn(`Failed to initialize satellite ${record.NORAD_CAT_ID}:`, error);
                return null;
            }
        }).filter(sat => sat !== null);

        console.log(`✓ Initialized ${this.satellites.length} satellite propagators`);
        return this.satellites;
    }

    // Get position of a satellite at a given time
    getPosition(satellite, date) {
        const positionAndVelocity = satellite.propagate(satellite.satrec, date);

        if (positionAndVelocity.error) {
            console.warn(`Propagation error for ${satellite.name}:`, positionAndVelocity.error);
            return null;
        }

        const positionEci = positionAndVelocity.position;

        if (!positionEci || typeof positionEci.x !== 'number') {
            return null;
        }

        // Convert ECI to geodetic coordinates (lat, lon, alt)
        const gmst = satellite.gstime(date);
        const positionGd = satellite.eciToGeodetic(positionEci, gmst);

        return {
            longitude: satellite.degreesLong(positionGd.longitude),
            latitude: satellite.degreesLat(positionGd.latitude),
            altitude: positionGd.height * 1000 // Convert km to meters
        };
    }

    // Get all satellite positions at current time
    getAllPositions(date = new Date()) {
        return this.satellites.map(sat => {
            const position = this.getPosition(sat, date);
            return {
                satellite: sat,
                position: position
            };
        }).filter(item => item.position !== null);
    }
}

// Export for use in main script
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SatelliteManager;
}
