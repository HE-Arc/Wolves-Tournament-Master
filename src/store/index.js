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
    token: localStorage.getItem('wtm-token'),
    nbrNotif: 0,
    apiUrl: 'http://localhost:8000/api/',
    navigationDrawer: false,
    updateTournamentBracket: true
  },
  mutations: {
    /**
     * Set the current authenticated user
     *
     * @param {State} state state that contain the informations
     * @param {Object} authUser authenticated user's informations to save
     */
    setAuthUser(
      state,
      { authUserId, authUserEmail, authUserName, isAuthenticated }
    ) {
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

    /**
     * Set current authenticated user's token
     *
     * @param {State} state state that contain the informations
     * @param {String} newToken token to save
     */
    setToken(state, newToken) {
      // TODO: For security purposes, take localStorage out of the project.
      localStorage.setItem('wtm-token', newToken)
      state.token = newToken
    },

    /**
     * Logout the current authenticated user
     *
     * @param {State} state state that contain the informations
     */
    logout(state) {
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
    },

    /**
     * Update current authenticated user's notifications
     *
     * @param {State} state state that contain the informations
     * @param {Integer} newNumber
     */
    updateNotif(state, newNumber) {
      state.nbrNotif = newNumber
    },

    /**
     * Set the navigation drawer (on or off)
     *
     * @param {State} state state that contain the informations
     */
    setNavigationDrawer(state) {
      state.navigationDrawer = !state.navigationDrawer
    },

    /**
     * Set if the tournament bracket need to be updated (yes or no)
     *
     * @param {State} state state that contain the informations
     */
    setUpdateTournamentBracket(state) {
      state.updateTournamentBracket = !state.updateTournamentBracket
    }
  },
  actions: {},
  modules: {},
  getters: {
    /**
     * Return the authorization header for the API
     *
     * @param {State} state state that contain the informations
     * @returns {Object} Authorization header
     */
    getAxiosHeader: state => {
      return { Authorization: `Token ${state.token}` }
    }
  }
})
