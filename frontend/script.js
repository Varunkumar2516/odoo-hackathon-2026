function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const message = document.getElementById("message");

  if (email === "" || password === "") {
    message.textContent = "Please enter email and password.";
    message.style.color = "red";
  } else {
    message.textContent = "Login Successful!";
    message.style.color = "green";

    // Later you can redirect to the dashboard
    // window.location.href = "dashboard.html";
  }
}