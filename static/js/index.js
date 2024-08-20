const carForm = document.getElementById("carForm");
const carList = document.getElementById("carList");

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

function handleScroll() {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
    updateCarList();
  }
}

window.addEventListener('scroll', handleScroll);

// Initial load
updateCarList();

carForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const descriptionSize = document.getElementById("descriptionSize").value;
  
    // Call /register endpoint with the car model
    fetch('/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({desc_size: descriptionSize}),
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
