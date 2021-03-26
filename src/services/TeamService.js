import axios from 'axios'

export default {
    apiurl: 'http://localhost:8000/api/',

    GetTeams() {
        return new Promise(resolve => {
            axios
                .get(this.apiurl + 'teams/')
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    GetTeamById(id) {
        return new Promise(resolve => {
            axios
                .get(this.apiurl + 'teams/' + id + '/')
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    GetTeamsByMember(token, member) {
        return new Promise(resolve => {
            let config = {
                headers: {
                    Authorization: 'Token' + token
                }
            }
            axios
                .get(this.apiurl + 'teams?uid=' + member, config)
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    CreateTeam(team) {
        return new Promise(resolve => {
            axios
                .post(this.apiurl + 'teams/', team)
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    UpdateTeam(token, team) {
        return new Promise(resolve => {
            let config = {
                headers: {
                    Authorization: 'Token' + token
                }
            }

            axios
                .put(this.apiurl + 'teams/' + team.id + '/', team, config)
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    DeleteTeam(token, team) {
        return new Promise(resolve => {
            let config = {
                headers: {
                    Authorization: 'Token' + token
                }
            }

            axios
                .delete(this.apiurl + 'teams/' + team.id + '/', config)
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    AddUser(token, uid, tid){
        return new Promise(resolve => {
            let data = {
                userid: uid
            }
            let config = {
                headers: {
                    Authorization: 'Token' + token
                }
            }
            axios
                .post(this.apiurl + 'teams/' + tid + "/adduser/", data, config)
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    }
}
