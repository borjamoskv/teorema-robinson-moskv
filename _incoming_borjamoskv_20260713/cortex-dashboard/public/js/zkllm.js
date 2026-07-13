// zkllm.js - Interactive ZK-ML Forensics Logic for tlookup & zkLLM

document.addEventListener('DOMContentLoaded', () => {
    initTabsNavigation();
});

// Navigation Logic
function initTabsNavigation() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;

            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetElement = document.getElementById(targetTab);
            if (targetElement) {
                targetElement.classList.add('active');
                
                // Trigger chart rendering when the ZK tab becomes active
                if (targetTab === 'tab-zkllm') {
                    renderCharts();
                }
            }
        });
    });
}

let chartsInitialized = false;

function renderCharts() {
    if (chartsInitialized) return; // Prevent multiple initializations
    chartsInitialized = true;

    // 1. Chart.js: tlookup Parallel Efficiency vs Competitors
    renderParallelEfficiencyChart();

    // 2. Plotly: Double Axis GPU Proving vs CPU Verification
    renderDoubleAxisPerformanceChart();
}

function renderParallelEfficiencyChart() {
    const ctx = document.getElementById('parallelEfficiencyChart').getContext('2d');

    // Labels wrapped into arrays of strings for multi-line support
    const labels = [
        ['tlookup', '(zkLLM Parallel CUDA)'],
        ['Lasso Lookup', '(Jolt-based Framework)'],
        ['LogUp', '(cq/Multiset Logarithmic)'],
        ['Plookup', '(Plonkish Monolithic)']
    ];

    const throughputData = [120, 15, 8, 1.5]; // in Millions of lookups per second (M/s)

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Throughput de Búsqueda (M ops/seg)',
                data: throughputData,
                backgroundColor: [
                    'rgba(43, 59, 229, 0.75)',  // Electric Blue
                    'rgba(138, 43, 226, 0.6)',  // Radiant Violet
                    'rgba(138, 43, 226, 0.3)',  // Translucent Violet
                    'rgba(255, 255, 255, 0.05)' // Sleek Dark Gray
                ],
                borderColor: [
                    '#2b3be5',
                    '#8a2be2',
                    'rgba(138, 43, 226, 0.6)',
                    'rgba(255, 255, 255, 0.2)'
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(6, 7, 19, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#9ca3af',
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        title: function(context) {
                            // Reassemble multiline labels for the tooltip title
                            return context[0].label.replace(/,/g, ' ');
                        },
                        label: function(context) {
                            return ` Throughput: ${context.parsed.y} M ops/s`;
                        },
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            const tips = [
                                "Velocidad SOTA: Optimización masiva CUDA sobre GPU.",
                                "Lasso rinde bien, pero carece del pipeline optimizado de tensores de zkLLM.",
                                "LogUp en GPU sufre sobrecarga asintótica en el sumcheck multiset.",
                                "Plookup convencional carece de diseño enfocado en hardware paralelo."
                            ];
                            return "\n" + tips[index];
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)'
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)'
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: {
                            family: 'Inter'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Millones de Operaciones / Segundo',
                        color: '#9ca3af',
                        font: {
                            family: 'Outfit',
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

function renderDoubleAxisPerformanceChart() {
    const traceGPU = {
        x: ['LLaMA-2 7B', 'LLaMA-2 13B'],
        y: [120, 245], // Proving Time in seconds (GPU)
        name: 'Tiempo Prueba GPU (s)',
        type: 'bar',
        marker: {
            color: 'rgba(43, 59, 229, 0.7)',
            line: {
                color: '#2b3be5',
                width: 1.5
            }
        }
    };

    const traceCPU = {
        x: ['LLaMA-2 7B', 'LLaMA-2 13B'],
        y: [0.045, 0.088], // Verification Time in seconds (CPU)
        name: 'Verificación CPU (s)',
        yaxis: 'y2',
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: '#8a2be2',
            width: 3
        },
        marker: {
            color: '#a04ef6',
            size: 10,
            line: {
                color: '#fff',
                width: 1.5
            }
        }
    };

    const data = [traceGPU, traceCPU];

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        showlegend: true,
        legend: {
            x: 0.1,
            y: 1.1,
            orientation: 'h',
            font: {
                color: '#9ca3af',
                family: 'Inter'
            }
        },
        margin: { t: 40, b: 40, l: 50, r: 50 },
        xaxis: {
            gridcolor: 'rgba(255, 255, 255, 0.03)',
            tickfont: {
                color: '#9ca3af',
                family: 'Outfit',
                size: 12
            }
        },
        yaxis: {
            title: 'Tiempo de Generación de Pruebas (s)',
            titlefont: { color: '#4e5dff', family: 'Outfit' },
            tickfont: { color: '#9ca3af' },
            gridcolor: 'rgba(255, 255, 255, 0.03)'
        },
        yaxis2: {
            title: 'Tiempo de Verificación (s)',
            titlefont: { color: '#a04ef6', family: 'Outfit' },
            tickfont: { color: '#9ca3af' },
            overlaying: 'y',
            side: 'right',
            gridcolor: 'rgba(255, 255, 255, 0.01)'
        }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot('doubleAxisPerformanceChart', data, layout, config);
}
