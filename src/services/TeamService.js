import axios from "axios";

export default {
  apiurl: "http://localhost:8000/",

  GetTeams() {
    return new Promise(resolve => {
      axios.get(this.apiurl + "teams/")
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
  CreateTeam(team) {
    return new Promise(resolve => {
      axios.post(this.apiurl + "teams/", team)
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
  DeleteTeam(token, team) {
    return new Promise(resolve => {
      let config = {
        headers : {
          'Authorization': 'Token' + token
        }
      };

      axios.delete(this.apiurl + "teams/" + team.id, config)
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
