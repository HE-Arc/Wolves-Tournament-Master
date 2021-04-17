import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import veevalidate from 'vee-validate'
import VueMeta from 'vue-meta'

import snotify from 'vue-snotify'
import 'vue-snotify/styles/material.css'

Vue.config.productionTip = false

Vue.use(snotify)
Vue.use(veevalidate)
Vue.use(VueMeta, {
  refreshOnceOnNavigation: true
})

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
