document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch and display stock prices
    function fetchStockPrices() {
        fetch('/get-stock-prices')
            .then(response => response.json())
            .then(data => {
                const stockTable = document.getElementById('stock-table');
                stockTable.innerHTML = ''; // Clear the table
                for (const symbol in data) {
                    const stockData = data[symbol];
                    const row = `<tr>
                        <td>${symbol}</td>
                        <td>${stockData.price}</td>
                        <td>${stockData.last_updated}</td>
                    </tr>`;
                    stockTable.innerHTML += row;
                }
            })
            .catch(error => {
                console.error('Error fetching stock prices:', error);
            });
    }

    // Initial fetch and update every 5 minutes (300000 ms)
    fetchStockPrices();
    setInterval(fetchStockPrices, 300000);
});
