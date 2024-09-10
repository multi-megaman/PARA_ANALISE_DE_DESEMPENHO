const carForm = document.getElementById("carForm");
const carList = document.getElementById("carList");
const totalCarsElement = document.getElementById('totalCars');

let offset = 0;
const limit = 20;
let isLoading = false;

function updateCarList() {
  if (isLoading) return;
  isLoading = true;

  fetch(`/cars?offset=${offset}&limit=${limit}`)
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      data.forEach((car, index) => {
        const li = document.createElement("li");
        li.textContent = `${offset + index + 1}. ${car.plate} | ${car.description}`;
        carList.appendChild(li);
      });
      offset += limit;
      isLoading = false;
    })
    .catch(error => {
      console.error('Error:', error);
      isLoading = false;
    });
}

function updateTotalCars() {
  fetch('/cars/count')
    .then(response => response.json())
    .then(data => {
      totalCarsElement.textContent = data.total_cars;
    })
    .catch(error => {
      console.error('Error:', error);
    });
}


// Initial load
updateCarList();
updateTotalCars();

// Handle infinite scrolling
window.addEventListener('scroll', () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500 && !isLoading) {
    updateCarList();
  }
});

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
      body: JSON.stringify({description: carDescription, plate: carPlate}),
    })
    .then(response => response.json())
    .then(data => {
      // Update cars array and only after successful registration
      updateCarList();
      updateTotalCars();
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  
    carForm.reset();
  });


//call the delete endpoint
document.getElementById('deleteButton').addEventListener('click', function() {
  const password = prompt('Enter password to delete all cars:');

  if (!password) {
    alert('Password is required.');
    return;
  }

  fetch('/cars/delete', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ password: password })
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
    } else {
      alert(data.message);
      document.getElementById('totalCars').innerText = '0';
      document.getElementById('carList').innerHTML = '';
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
});

//call the reset_resources endpoint
document.getElementById('resetResourcesButton').addEventListener('click', function() {
  const password = prompt('Enter password to reset resources:');

  if (!password) {
    alert('Password is required.');
    return;
  }

  fetch('/reset_resources', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ password: password })
  })
  .then(response => response.json())
  .then(data => { 
    alert(data.message);
  })
  .catch(error => {
    console.error('Error:', error);
  });
}); 

// Include the Socket.IO client library
const socket = io();

// Listen for the car_count_update event
socket.on('car_count_update', function(data) {
  console.log('Total cars:', data.total_cars);
  // Update the totalCarsElement with the new car count
  totalCarsElement.textContent = `Total Cars: ${data.total_cars}`;
});

// Listen for the new_car event
socket.on('new_car', function(data) {
  console.log('New car:', data);
  // Add the new car to the car list
  const li = document.createElement("li");
  li.textContent = `${data.id}. ${data.plate} | ${data.description}`;
  carList.appendChild(li);
  offset += 1;
});