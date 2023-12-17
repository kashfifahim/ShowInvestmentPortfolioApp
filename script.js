document.addEventListener('DOMContentLoad', function() {
    fetchStockPrice();
});


function fetchStockPrice() {
	const apiKey = "Z26IND1A7LZTHK7V";
	const symbol = 'AAPL';
	const url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${apiKey}';

	fetch(url)
		.then(response => response.json())
		.then(data => {
			print(data)
			const price = data['Global Quote']['05. price'];
			document.getElementById('stock-price').innerText = '$${parseFloat(price).toFixed(2)}';})
		.catch(error => {
			console.error('Error fetching stock data:', erorr);
			document.getElementById('stock-price').innerText = 'Sorry Problem Loading Data';
		});
}
