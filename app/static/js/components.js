document.addEventListener("alpine:init", () => {
  Alpine.data("register", () => ({
    message: "",
    showUsernameError: false,
    showRepeatPasswordError: false,
    showPasswordError: false,
    showPassword: false,
    showSubmitButton: false,
    showServerError: false,
    username: "",
    password: "",
    repeatPassword: "",
    emailPattern: /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/,
    passwordPattern: /^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$/,
    checkUsername() {
      if (!this.username) {
        this.showUsernameError = false;
      } else if (!this.emailPattern.test(this.username)) {
        this.showUsernameError = true;
        this.showPassword = false;
      } else {
        this.showUsernameError = false;
        this.showPassword = true;
      }
    },
    passwordsMatch() {
      if (!this.repeatPassword) {
        this.showRepeatPasswordError = false;
        this.showSubmitButton = true;
      } else if (this.password !== this.repeatPassword) {
        this.showRepeatPasswordError = true;
      } else {
        this.showRepeatPasswordError = false;
        this.showSubmitButton = false;
      }
    },
    validatePassword() {
      if (!this.password) {
        this.showPasswordError = false;
      } else if (!this.passwordPattern.test(this.password)) {
        this.showPasswordError = true;
      } else {
        this.showPasswordError = false;
      }
    },
    disableButton() {
      this.showSubmitButton = true;
    },
    checkServerError() {
      if (this.showServerError) {
        setTimeout(() => {
          this.showServerError = false;
        }, 3000);
      }
    },
    async registerUser() {
      if (!this.username || !this.password || !this.repeatPassword) {
        alert("Please fill in all fields");
        return;
      }
      if (this.password !== this.repeatPassword) {
        alert("Passwords do not match");
        return;
      }
      const formData = {
        email: this.username,
        password: this.password,
      };
      try {
        const response = await fetch("/auth/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });
        if (response.status === 201) {
          this.message = "User created successfully";
          this.showServerError = true;
          setTimeout(() => {
            window.location.href = "/";
          }, 1000);
        } else if (response.status === 400) {
          this.message = "User already exists";
          this.showServerError = true;
        }
      } catch (error) {
        console.error("Error:", error);
      }
    },
  }));
});

document.addEventListener("alpine:init", () => {
  // Alpine component to control the login form and other attributes for login page
  Alpine.data("login", () => ({
    username: "",
    password: "",
    message: "",
    showError: false,
    showUsernameError: false,
    showPasswordDiv: false,
    showInputButton: false,
    csrfToken: "",

    checkLoginUsername() {
      const emailPattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
      if (this.username === "") {
        this.showUsernameError = true;
      } else if (!emailPattern.test(this.username)) {
        this.showUsernameError = true;
      } else {
        this.showUsernameError = false;
        this.showPasswordDiv = true;
      }
    },

    allocateCSRFToken(value) {
      this.csrfToken = value;
    },
    setCookie() {
      const formData = new URLSearchParams();
      formData.append("grant_type", "");
      formData.append("username", this.username);
      formData.append("password", this.password);
      formData.append("scope", "");
      formData.append("client_id", "");
      formData.append("client_secret", "");

      fetch("/auth/jwt/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRF-Token": this.csrfToken,
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
            return response.text();
          }
        })
        .then((errorMessage) => {
          if (errorMessage) {
            console.log(errorMessage);
          }
        });
    },
  }));
});

/**
 * Listens for the "showAlert" event on the document.body and updates the data of the "upload-page" component accordingly.
 * If the event detail has a "type" property of "updated", "added", or "deleted",
 * it sets the corresponding data properties on the "upload-page" component.
 * The data properties set are "isUpdated", "isAdded", and "isDeleted" respectively, and the "message" property is set to the value of the "message" property in the event detail.
 * If the "upload-page" component is not found, an error is logged to the console.
 */
document.body.addEventListener("showAlert", function (evt) {
  try {
    console.log("showAlert event received in Component.js");
    const source = evt.detail.source;
    const components = document.querySelectorAll("[x-data]");

    const uploadPageIndex = Array.from(components).findIndex(
      (component) => component.id === source
    );

    if (uploadPageIndex === -1) {
      throw new Error("No element with id 'upload-page' found");
    }
    const component = components[uploadPageIndex];
    if (!component) {
      throw new Error("No element with x-data found");
    }
    const data = Alpine.mergeProxies(component._x_dataStack);
    setTimeout(function () {
      if (evt.detail.type == "updated") {
        data.isUpdated = true;
        data.message = evt.detail.message;
      } else if (evt.detail.type == "added") {
        data.isAdded = true;
        data.message = evt.detail.message;
      } else if (evt.detail.type == "deleted") {
        data.isDeleted = true;
        data.message = evt.detail.message;
      }
    }, 1000);
  } catch (error) {
    console.error("Error in message display:", error);
  }
});
