const dates = {{ dates|safe }};
const buys = {{ buys|safe }};
const pie_labels = {{ pie_labels|safe }};
const pie_values = {{ pie_values|safe }};

// Initialize Area Chart
const ctxArea = document.getElementById('myAreaChart').getContext('2d');
new Chart(ctxArea, {
    // ... (rest of the Area Chart configuration)
});

// Initialize Pie Chart
const ctxPie = document.getElementById('myPieChart').getContext('2d');
new Chart(ctxPie, {
    // ... (rest of the Pie Chart configuration)
});