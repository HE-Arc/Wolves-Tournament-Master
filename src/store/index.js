import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        authUser: JSON.parse(localStorage.getItem('wtm-authuser')) || {
            id: null,
            email: null,
            name: null,
            team: null,
            isAuthenticated: false
        },
        token: localStorage.getItem('wtm-token')
    },
    mutations: {
        setAuthUser(state, { authUserId, authUserEmail, authUserName, isAuthenticated }) {
            state.authUser = {
                id: authUserId,
                email: authUserEmail,
                name: authUserName,
                team: null,
                isAuthenticated: isAuthenticated
            }
            // TODO: For security purposes, take localStorage out of the project.
            localStorage.setItem('wtm-authuser', JSON.stringify(state.authUser))
        },
        setToken(state, newToken) {
            // TODO: For security purposes, take localStorage out of the project.
            localStorage.setItem('wtm-token', newToken)
            state.token = newToken
        },
        removeToken(state) {
            // TODO: For security purposes, take localStorage out of the project.
            localStorage.removeItem('wtm-token')
            localStorage.removeItem('wtm-authuser')
            state.token = null
            state.authUser = {
                id: null,
                email: null,
                name: null,
                team: null,
                isAuthenticated: false
            }
        }
    },
    actions: {},
    modules: {}
})
