import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";

import snotify from 'vue-snotify';

Vue.config.productionTip = false;

Vue.use(snotify);

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount("#app");
