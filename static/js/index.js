function sendRequest() {
  var complexity = document.getElementById('complexity').value;
  if (complexity < 1 || complexity > 10) {
      alert('Please enter a complexity between 1 and 10.');
      return;
  }
  
  fetch('/process', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ complexity: parseInt(complexity) }),
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById('result').innerHTML = 'Result: ' + data.result;
  })
  .catch((error) => {
      console.error('Error:', error);
  });
}