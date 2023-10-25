export function setCookie(username, password) {
  const formData = new URLSearchParams();
  formData.append("grant_type", "");
  formData.append("username", username);
  formData.append("password", password);
  formData.append("scope", "");
  formData.append("client_id", "");
  formData.append("client_secret", "");

  fetch("/auth/jwt/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  })
    .then((response) => {
      if (response.status === 204) {
        // Successful login, navigate to /dashboard
        window.location.href = "/dashboard";
      } else if (response.status === 400) {
        // Incorrect username or password
        this.message = "Incorrect username or password";
        this.showError = true;
      }
    })
    .then((errorMessage) => {
      if (errorMessage) {
        Alpine.store("message", "Error: Incorrect username or password");
        console.log(errorMessage);
      }
    });

  Alpine.data("login", () => ({
    setCookie,
  }));
}
