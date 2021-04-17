import axios from 'axios'

export default {
  /**
   * Generic axios request
   * 
   * @param {String} method method ('get', 'post', 'put', 'delete', ...)
   * @param {String} url url of the API to call (this.$store.state.apiUrl + '/teams/')
   * @param {Object} data data that we want to pass to the API ({ firstName: 'Fred', lastName: 'Flintstone'})
   * @param {Object} headers header to integrate the token to authorize methods in the API (this.$store.getters.getAxiosHeader)
   */
  Request(method, url, data = null, header = null) {
    return new Promise(resolve => {
      axios({
        method: method, 
        url: url,
        data: data,
        headers: header 
      })
        .then(response => {
          resolve({ isSuccess: true, result: response.data })
        })
        .catch(error => {
          resolve({ isSuccess: false, result: error })
        })
    })
  },

  /**
   * Request to get notifications and compute the number of unseen one
   * 
   * @param {String} url url of the API to call
   * @param {Object} header header to integrate the token to authorize methods in the API
   */
  GetNotifications(url, header) {
    return new Promise(resolve => {
      axios({
        method: 'get',
        url: url,
        headers: header
      })
        .then(response => {
          let notifNumber = response.data.filter(n => n.seen == false).length

          resolve({
            isSuccess: true,
            result: response.data,
            counter: notifNumber
          })
        })
        .catch(error => {
          resolve({ isSuccess: false, result: error })
        })
    })
  }
}
