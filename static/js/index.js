const carForm = document.getElementById("carForm");
const carList = document.getElementById("carList");

function updateCarList() {
    fetch('/cars')
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
        carList.innerHTML = "";
        data.forEach((car, index) => {
          const li = document.createElement("li");
          li.textContent = `${index + 1}. ${car.plate} | ${car.description}`;
          carList.appendChild(li);
        });
      })
      .catch(error => console.error('Error:', error));
  }

carForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const carDescription = document.getElementById("carDescription").value;
    const carPlate = document.getElementById("carPlate").value;
  
    // Call /register endpoint with the car model
    fetch('/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({plate: carPlate, description: carDescription }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      // Update cars array and only after successful registration
      updateCarList();
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  
    carForm.reset();
  });

updateCarList();