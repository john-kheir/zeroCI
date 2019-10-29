import Vue from 'vue'
import App from './App'
import router from './router'

import Default from "./layouts/Default.vue"

Vue.component('default-layout', Default)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  router,
  render: h => h(App)
}).$mount("#wrapper");
