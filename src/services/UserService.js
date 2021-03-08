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
  GetToken() {
    return new Promise(resolve => {
      axios
        .post(this.apiurl + "api-token-auth/")
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
      axios.defaults.xsrfCookieName = 'csrftoken'
      axios.defaults.xsrfHeaderName = 'X-CSRFToken'

      axios.post(this.apiurl + "api-token-auth/", user)
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
  GetAuthUser(token) {
    return new Promise(resolve => {
      axios.defaults.xsrfCookieName = 'csrftoken'
      axios.defaults.xsrfHeaderName = 'X-CSRFToken'


      axios({
        headers: {
        // Set your Authorization to 'JWT', not Bearer!!!
          Authorization: `JWT ${token}`,
          'Content-Type': 'application/json'
        },
        xhrFields: {
            withCredentials: true
        },
        method: "get",
        url: this.apiurl + "user/",
        data: {}
      })
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
};
