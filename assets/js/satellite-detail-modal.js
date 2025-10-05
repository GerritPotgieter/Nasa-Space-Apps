/**
 * Reusable Satellite Detail Modal Component
 * Usage: Include this JS file and call showSatelliteDetailModal(satelliteData)
 */

// Data sanitization helper function
function sanitizeValue(value, options = {}) {
    if (value === null || value === undefined || value === '') {
        return options.default || '-';
    }

    // Convert to string and trim
    let cleaned = String(value).trim();

    // Remove extra quotes
    cleaned = cleaned.replace(/^["']+|["']+$/g, '');

    // Remove multiple spaces
    cleaned = cleaned.replace(/\s+/g, ' ');

    // Handle common placeholder values
    if (cleaned === '' ||
        cleaned === 'null' ||
        cleaned === 'undefined' ||
        cleaned === 'N/A' ||
        cleaned === 'n/a' ||
        cleaned === '-' ||
        cleaned === '?') {
        return options.default || '-';
    }

    // Apply unit if provided
    if (options.unit && cleaned !== '-') {
        return `${cleaned} ${options.unit}`;
    }

    // Apply suffix if provided
    if (options.suffix && cleaned !== '-') {
        return `${cleaned}${options.suffix}`;
    }

    return cleaned;
}

// Format coordinates
function formatCoordinates(lat, lon) {
    const cleanLat = sanitizeValue(lat);
    const cleanLon = sanitizeValue(lon);

    if (cleanLat === '-' || cleanLon === '-') {
        return '-';
    }

    return `${cleanLat}°, ${cleanLon}°`;
}

// Global function to show the satellite detail modal
function showSatelliteDetailModal(satData) {
    if (!satData) return;

    // Populate modal header
    document.getElementById("modalSatName").textContent = sanitizeValue(satData.Name || satData.OBJECT_NAME, { default: 'Unknown Satellite' });

    // Identification
    document.getElementById("modal_name").textContent = sanitizeValue(satData.Name);
    document.getElementById("modal_jcat").textContent = sanitizeValue(satData.JCAT || satData.NORAD_CAT_ID);
    document.getElementById("modal_object_name").textContent = sanitizeValue(satData.OBJECT_NAME);
    document.getElementById("modal_launch_tag").textContent = sanitizeValue(satData.SatcatLaunch_Tag);
    document.getElementById("modal_type").textContent = sanitizeValue(satData.Type);
    document.getElementById("modal_status").textContent = sanitizeValue(satData.STATUS || satData.Status);

    // Ownership
    document.getElementById("modal_owner").textContent = sanitizeValue(satData.Owner);
    document.getElementById("modal_state").textContent = sanitizeValue(satData.State);
    document.getElementById("modal_org_name").textContent = sanitizeValue(satData.Org_Name);
    document.getElementById("modal_org_short").textContent = sanitizeValue(satData.Org_ShortName);
    document.getElementById("modal_org_location").textContent = sanitizeValue(satData.Org_Location);
    document.getElementById("modal_org_coords").textContent = formatCoordinates(satData.Org_Latitude, satData.Org_Longitude);
    document.getElementById("modal_manufacturer").textContent = sanitizeValue(satData.Manufacturer);

    // Launch Information
    document.getElementById("modal_ldate").textContent = sanitizeValue(satData.LDate);
    document.getElementById("modal_sdate").textContent = sanitizeValue(satData.SDate);
    document.getElementById("modal_odate").textContent = sanitizeValue(satData.ODate);
    document.getElementById("modal_ddate").textContent = sanitizeValue(satData.DDate);
    document.getElementById("modal_primary").textContent = sanitizeValue(satData.Primary);

    // Orbital Parameters
    document.getElementById("modal_perigee").textContent = sanitizeValue(satData.Perigee, { unit: 'km' });
    document.getElementById("modal_apogee").textContent = sanitizeValue(satData.Apogee, { unit: 'km' });
    document.getElementById("modal_inclination").textContent = sanitizeValue(satData.INCLINATION || satData.Inc, { suffix: '°' });
    document.getElementById("modal_eccentricity").textContent = sanitizeValue(satData.ECCENTRICITY);
    document.getElementById("modal_mean_motion").textContent = sanitizeValue(satData.MEAN_MOTION, { unit: 'rev/day' });
    document.getElementById("modal_epoch").textContent = sanitizeValue(satData.EPOCH);
    document.getElementById("modal_rev_epoch").textContent = sanitizeValue(satData.REV_AT_EPOCH);

    // Physical Characteristics
    document.getElementById("modal_mass").textContent = sanitizeValue(satData.Mass, { unit: 'kg' });
    document.getElementById("modal_drymass").textContent = sanitizeValue(satData.DryMass, { unit: 'kg' });
    document.getElementById("modal_totmass").textContent = sanitizeValue(satData.TotMass, { unit: 'kg' });
    document.getElementById("modal_length").textContent = sanitizeValue(satData.Length, { unit: 'm' });
    document.getElementById("modal_diameter").textContent = sanitizeValue(satData.Diamete, { unit: 'm' });
    document.getElementById("modal_span").textContent = sanitizeValue(satData.Span, { unit: 'm' });
    document.getElementById("modal_shape").textContent = sanitizeValue(satData.Shape);

    // Advanced Orbital Data
    document.getElementById("modal_ra_node").textContent = sanitizeValue(satData.RA_OF_ASC_NODE, { suffix: '°' });
    document.getElementById("modal_arg_peri").textContent = sanitizeValue(satData.ARG_OF_PERICENTER, { suffix: '°' });
    document.getElementById("modal_mean_anomaly").textContent = sanitizeValue(satData.MEAN_ANOMALY, { suffix: '°' });
    document.getElementById("modal_bstar").textContent = sanitizeValue(satData.BSTAR);
    document.getElementById("modal_mm_dot").textContent = sanitizeValue(satData.MEAN_MOTION_DOT);
    document.getElementById("modal_mm_ddot").textContent = sanitizeValue(satData.MEAN_MOTION_DDOT);
    document.getElementById("modal_element_set").textContent = sanitizeValue(satData.ELEMENT_SET_NO);

    // TLE Data (if available)
    const tleFetched = satData.TLE_FETCHED === 'YES';
    const tleSection = document.getElementById("tleSection");

    if (tleFetched) {
        tleSection.style.display = "block";
        document.getElementById("modal_tle_fetched").textContent = "✓ Yes";
        document.getElementById("modal_n2yo_name").textContent = sanitizeValue(satData.N2YO_SAT_NAME);
        document.getElementById("modal_tle_line1").textContent = sanitizeValue(satData.TLE_LINE1);
        document.getElementById("modal_tle_line2").textContent = sanitizeValue(satData.TLE_LINE2);
    } else {
        tleSection.style.display = "none";
    }

    // Show modal
    document.getElementById("detailModal").classList.add("active");
}

// Close detail modal
function closeDetailModal() {
    document.getElementById("detailModal").classList.remove("active");
}

// ESC key to close modal
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        closeDetailModal();
    }
});

// Click outside modal to close
document.addEventListener("click", (e) => {
    const modal = document.getElementById("detailModal");
    if (e.target === modal) {
        closeDetailModal();
    }
});
