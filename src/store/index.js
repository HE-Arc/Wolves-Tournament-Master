import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    authUserId: null,
    authUserEmail: null,
    isAuthenticated: false,
    token: localStorage.getItem('token')
  },
  mutations: {
    setAuthUser(state, {
      authUserId,
      authUserEmail,
      isAuthenticated,
    }) {
      Vue.set(state, 'authUserId', authUserId)
      Vue.set(state, 'authUserEmail', authUserEmail)
      Vue.set(state, 'isAuthenticated', isAuthenticated)
    },
    updateToken(state, newToken) {
      // TODO: For security purposes, take localStorage out of the project.
      localStorage.setItem('token', newToken);
      state.token = newToken;
    },
    removeToken(state) {
      // TODO: For security purposes, take localStorage out of the project.
      localStorage.removeItem('token');
      state.token = null;
    }
  },
  actions: {},
  modules: {}
});
