import axios from "axios";

export default {
  apiurl: "http://localhost:8000/api/",

  GetNotifications(token, userid) {
    return new Promise(resolve => {
      let config = {
        headers : {
          'Authorization': 'Token' + token
        }
      };

      axios.get(this.apiurl + "notifications?uid=" + userid, config)
      //axios.post(this.apiurl + "notifications/getbyuser/", {uid:userid}, config)
        .then(response => {
          resolve({isSuccess: true, result: response.data});
        })
        .catch(error => {
          resolve({isSuccess: false, result: error});
        });
    });
  }
};
