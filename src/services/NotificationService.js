import axios from "axios";

export default {
  apiurl: "http://localhost:8000/api/",

  GetNotifications() {
    return new Promise(resolve => {
      axios.get(this.apiurl + "notifications/")
        .then(response => {
          resolve({isSuccess: true, result: response.data});
        })
        .catch(error => {
          resolve({isSuccess: false, result: error});
        });
    });
  }
};
