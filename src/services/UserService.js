import axios from 'axios'

export default {
    apiurl: 'http://localhost:8000/api/',

    GetUsers() {
        return new Promise(resolve => {
            axios
                .get(this.apiurl + 'users/')
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    CreateUser(user) {
        return new Promise(resolve => {
            axios
                .post(this.apiurl + 'users/', user)
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    Login(user) {
        return new Promise(resolve => {
            axios
                .post(this.apiurl + 'auth/', user)
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    }
}
