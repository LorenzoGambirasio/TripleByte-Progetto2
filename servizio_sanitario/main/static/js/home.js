const statistiche = JSON.parse(document.getElementById('statistiche-data').textContent);
const topOspedali = JSON.parse(document.getElementById('top-ospedali-data').textContent);
const topPatologie = JSON.parse(document.getElementById('top-patologie-data').textContent);


new Chart(document.getElementById('ricoveriStatoChart'), { type: 'doughnut', data: { labels: statistiche.labels, datasets: [{ label: 'Stato Ricoveri', data: statistiche.data, backgroundColor: ['#198754', '#ffc107', '#dc3545', '#212529'], borderColor: '#fff', borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { padding: 20 } } } } });

new Chart(document.getElementById('ospedaliTopChart'), { type: 'bar', data: { labels: topOspedali.labels, datasets: [{ label: 'Attivi', data: topOspedali.attivi, backgroundColor: '#198754' }, { label: 'Dimessi', data: topOspedali.dimessi, backgroundColor: '#dc3545' }, { label: 'Trasferiti', data: topOspedali.trasferiti, backgroundColor: '#ffc107' }, { label: 'Deceduti', data: topOspedali.deceduti, backgroundColor: '#212529' },] }, options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true, beginAtZero: true }, y: { stacked: true } }, plugins: { legend: { display: true, position: 'top' } } } });

if (topPatologie.labels.length > 0) {
    new Chart(document.getElementById('topPatologieChart'), {
        type: 'bar',
        data: {
            labels: topPatologie.labels,
            datasets: [{
                label: 'Numero di Ricoveri',
                data: topPatologie.data,
                backgroundColor: 'rgba(128, 0, 32, 0.7)',
                borderColor: 'rgba(128, 0, 32, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                },
                y: {
                    ticks: {
                        callback: function (value) {
                            const label = this.getLabelForValue(value);
                            return label.length > 20 ? label.substring(0, 20) + '...' : label;
                        }
                    }
                }
            }
        }
    });
} else {
    const canvas = document.getElementById('topPatologieChart');
    const ctx = canvas.getContext('2d');
    ctx.font = '14px sans-serif';
    ctx.fillStyle = '#6c757d';
    ctx.textAlign = 'center';
    ctx.fillText('Nessun dato disponibile', canvas.width / 2, canvas.height / 2);
}