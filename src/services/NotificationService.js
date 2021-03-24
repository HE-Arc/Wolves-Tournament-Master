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
        .then(response => {
          let notifNumber = response.data.filter(
            n => n.seen == false
          ).length
          resolve({isSuccess: true, result: response.data, counter: notifNumber});
        })
        .catch(error => {
          resolve({isSuccess: false, result: error});
        });
    });
  },
  UpdateNotification(token, notification) {
    return new Promise(resolve => {
      let config = {
        headers : {
          'Authorization': 'Token' + token
        }
      };

      axios.put(this.apiurl + "notifications/" + notification.id + "/", notification, config)
        .then(response => {
          resolve({isSuccess: true, result: response.data});
        })
        .catch(error => {
          resolve({isSuccess: false, result: error});
        });
    });
  }
};
