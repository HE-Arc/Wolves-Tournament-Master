import axios from "axios";

export default {
  apiurl: "http://localhost:8000/",

  GetUsers() {
    return new Promise(resolve => {
      axios
        .get(this.apiurl + "users/")
        .then(response => {
          if (response.data) {
            resolve(response.data);
          } else {
            resolve("Error");
          }
        })
        .catch(error => {
          resolve(error);
        });
    });
  },
  CreateUser(user) {
    return new Promise(resolve => {
      axios.post(this.apiurl + "users/", user)
        .then(response => {
          if (response.data) {
            resolve(response.data);
          } else {
            resolve("Error");
          }
        })
        .catch(error => {
          resolve(error);
        });
    });
  },
  Login(user) {
    return new Promise(resolve => {
      axios.post(this.apiurl + "auth/", user)
        .then(response => {
          if (response.data) {
            console.log(response.data)
            resolve(response.data);
          } else {
            resolve("Error");
          }
        })
        .catch(error => {
          resolve(error);
        });
    });
  }
};
