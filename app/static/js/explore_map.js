// Public Explore Map with GeoJSON & Filter Sync (Leaflet)

document.addEventListener('DOMContentLoaded', () => {
    const mapElement = document.getElementById('explore-map');
    if (!mapElement) return;

    // Default center
    const map = L.map('explore-map').setView([12.9716, 77.5946], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Color definitions by status
    const statusColors = {
        'submitted': '#f59e0b',
        'under_review': '#0284c7',
        'in_progress': '#0d9488',
        'resolved': '#10b981',
        'rejected': '#ef4444'
    };

    // Extract current URL filter parameters
    const urlParams = new URLSearchParams(window.location.search);
    const apiUrl = `/api/v1/issues/geojson?${urlParams.toString()}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const markers = [];

            if (!data.features || data.features.length === 0) {
                return;
            }

            L.geoJSON(data, {
                pointToLayer: (feature, latlng) => {
                    const status = feature.properties.status;
                    const color = statusColors[status] || '#0d9488';

                    const marker = L.circleMarker(latlng, {
                        radius: 9,
                        fillColor: color,
                        color: '#ffffff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.85
                    });
                    markers.push(latlng);
                    return marker;
                },
                onEachFeature: (feature, layer) => {
                    const p = feature.properties;
                    const statusBadgeClass = `badge-status-${p.status}`;
                    const formattedStatus = p.status.replace('_', ' ').toUpperCase();

                    let imgHtml = '';
                    if (p.image_before) {
                        imgHtml = `<img src="/static/${p.image_before}" style="width:100%; height:110px; object-fit:cover; border-radius:6px; margin-bottom:8px;" alt="Issue Preview">`;
                    }

                    const popupContent = `
                        <div style="font-family: inherit; width: 230px;">
                            ${imgHtml}
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <span class="badge ${statusBadgeClass}" style="font-size:0.7rem;">${formattedStatus}</span>
                                <small class="text-muted fw-bold">${p.tracking_id}</small>
                            </div>
                            <h6 style="margin: 4px 0; font-size:0.9rem; font-weight:700; color:#0b192c;">${p.title}</h6>
                            <p style="margin: 2px 0 6px; font-size:0.75rem; color:#64748b;">
                                <i class="bi bi-geo-alt"></i> ${p.address}
                            </p>
                            <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
                                <small class="text-muted"><i class="bi bi-hand-thumbs-up"></i> ${p.upvotes_count} votes</small>
                                <a href="/citizen/reports/${p.id}" class="btn btn-sm btn-primary py-0 px-2" style="font-size:0.75rem;">View Report</a>
                            </div>
                        </div>
                    `;

                    layer.bindPopup(popupContent);
                }
            }).addTo(map);

            if (markers.length > 0) {
                const bounds = L.latLngBounds(markers);
                map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
            }
        })
        .catch(err => {
            console.error('Failed to load map points:', err);
        });

    setTimeout(() => { map.invalidateSize(); }, 300);
});
