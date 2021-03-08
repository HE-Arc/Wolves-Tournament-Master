import axios from "axios";

export default {
  apiurl: "http://localhost:8000/",

  GetTeams() {
    return new Promise(resolve => {
      axios
        .get(this.apiurl + "teams/")
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
  CreateTeam(csrftoken, team) {
    return new Promise(resolve => {
      axios({
        headers: {'X-CSRFToken': csrftoken},
        method: "post",
        url: this.apiurl + "teams/",
        data: team
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
  }
};
