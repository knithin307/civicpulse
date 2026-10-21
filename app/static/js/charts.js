// CivicPulse Real-Time Chart.js Data Visualizations

document.addEventListener('DOMContentLoaded', () => {
    const categoryChartCanvas = document.getElementById('categoryChart');
    const monthlyTrendCanvas = document.getElementById('monthlyTrendChart');
    const statusChartCanvas = document.getElementById('statusChart');
    const priorityChartCanvas = document.getElementById('priorityChart');

    if (!categoryChartCanvas && !monthlyTrendCanvas && !statusChartCanvas) return;

    // Fetch real metrics from the REST API endpoint
    fetch('/api/v1/analytics/stats')
        .then(res => res.json())
        .then(data => {
            // 1. Category Breakdown Chart
            if (categoryChartCanvas && data.categories) {
                new Chart(categoryChartCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: data.categories.labels,
                        datasets: [{
                            data: data.categories.data,
                            backgroundColor: [
                                '#0d9488', '#3b82f6', '#f59e0b', '#10b981',
                                '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'
                            ],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { boxWidth: 12, font: { size: 11 } }
                            }
                        },
                        cutout: '65%'
                    }
                });
            }

            // 2. Monthly Trend (Created vs Resolved) Chart
            if (monthlyTrendCanvas && data.monthly_trend) {
                new Chart(monthlyTrendCanvas, {
                    type: 'line',
                    data: {
                        labels: data.monthly_trend.labels,
                        datasets: [
                            {
                                label: 'Issues Reported',
                                data: data.monthly_trend.created,
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                tension: 0.3,
                                fill: true,
                                pointRadius: 4
                            },
                            {
                                label: 'Issues Resolved',
                                data: data.monthly_trend.resolved,
                                borderColor: '#10b981',
                                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                tension: 0.3,
                                fill: true,
                                pointRadius: 4
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'top' }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { precision: 0 }
                            }
                        }
                    }
                });
            }

            // 3. Status Breakdown Bar Chart
            if (statusChartCanvas && data.statuses) {
                new Chart(statusChartCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.statuses.labels,
                        datasets: [{
                            label: 'Issues Count',
                            data: data.statuses.data,
                            backgroundColor: [
                                '#f59e0b', '#0284c7', '#0d9488', '#10b981', '#ef4444'
                            ],
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { precision: 0 }
                            }
                        }
                    }
                });
            }

            // 4. Priority Breakdown Chart
            if (priorityChartCanvas && data.priorities) {
                new Chart(priorityChartCanvas, {
                    type: 'pie',
                    data: {
                        labels: data.priorities.labels,
                        datasets: [{
                            data: data.priorities.data,
                            backgroundColor: ['#94a3b8', '#0284c7', '#f59e0b', '#ef4444'],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }
        })
        .catch(err => console.error('Failed to render analytics charts:', err));
});
