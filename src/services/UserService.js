import axios from "axios";

export default {
  apiurl: "http://localhost:8000/",

  GetUsers() {
    return new Promise(resolve => {
      axios
        .get(this.apiurl + "users")
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
  }
};
