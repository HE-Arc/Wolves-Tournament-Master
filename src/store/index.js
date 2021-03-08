import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    authUser: {},
    isAuthenticated: false,
    token: localStorage.getItem('token'),
  },
  mutations: {
    setAuthUser(state, {
      authUser,
      isAuthenticated,
    }) {
      Vue.set(state, 'authUser', authUser)
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
