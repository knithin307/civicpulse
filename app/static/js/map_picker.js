// Map Picker for Civic Issue Reporting (Leaflet)

document.addEventListener('DOMContentLoaded', () => {
    const mapElement = document.getElementById('map-picker');
    if (!mapElement) return;

    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const addressInput = document.getElementById('address');
    const coordsDisplay = document.getElementById('coords-display');
    const detectBtn = document.getElementById('btn-detect-location');

    // Default coordinates (e.g. Metro Center)
    let initialLat = parseFloat(latInput.value) || 12.9716;
    let initialLng = parseFloat(lngInput.value) || 77.5946;

    const map = L.map('map-picker').setView([initialLat, initialLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Custom marker icon
    const marker = L.marker([initialLat, initialLng], {
        draggable: true,
        autoPan: true
    }).addTo(map);

    function updateCoordinates(lat, lng) {
        lat = parseFloat(lat.toFixed(6));
        lng = parseFloat(lng.toFixed(6));
        latInput.value = lat;
        lngInput.value = lng;
        if (coordsDisplay) {
            coordsDisplay.textContent = `Coordinates: ${lat}, ${lng}`;
        }
    }

    // Initialize values
    updateCoordinates(initialLat, initialLng);

    // When marker is dragged
    marker.on('dragend', (e) => {
        const position = marker.getLatLng();
        updateCoordinates(position.lat, position.lng);
    });

    // When map is clicked
    map.on('click', (e) => {
        marker.setLatLng(e.latlng);
        updateCoordinates(e.latlng.lat, e.latlng.lng);
    });

    // Geolocation detector button
    if (detectBtn) {
        detectBtn.addEventListener('click', () => {
            if (!navigator.geolocation) {
                alert('Geolocation is not supported by your browser.');
                return;
            }

            detectBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Locating...';
            detectBtn.disabled = true;

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const userLat = position.coords.latitude;
                    const userLng = position.coords.longitude;
                    map.setView([userLat, userLng], 16);
                    marker.setLatLng([userLat, userLng]);
                    updateCoordinates(userLat, userLng);

                    detectBtn.innerHTML = '<i class="bi bi-geo-alt-fill me-1 text-success"></i> Location Found';
                    detectBtn.disabled = false;
                },
                (error) => {
                    alert('Unable to retrieve your location. Please select it manually on the map.');
                    detectBtn.innerHTML = '<i class="bi bi-crosshair me-1"></i> Detect My Location';
                    detectBtn.disabled = false;
                },
                { enableHighAccuracy: true, timeout: 8000 }
            );
        });
    }

    // Force map size refresh when rendered inside tab or accordion
    setTimeout(() => { map.invalidateSize(); }, 300);
});
