import axios from 'axios'

export default {
    apiurl: 'http://localhost:8000/api/',

    GetTournaments() {
        return new Promise(resolve => {
            axios
                .get(this.apiurl + 'tournaments/')
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
    CreateTournament(tournament) {
        return new Promise(resolve => {
            axios
                .post(this.apiurl + 'tournaments/', tournament)
                .then(response => {
                    resolve({ isSuccess: true, result: response.data })
                })
                .catch(error => {
                    resolve({ isSuccess: false, result: error })
                })
        })
    },
}
