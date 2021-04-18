import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Administration from '../views/Administration.vue'
import Team from '../views/Team.vue'
import Register from '../views/Register.vue'
import Tournament from '../views/Tournament.vue'
import Notifications from '../views/Notifications.vue'
import About from '../views/About.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/administration',
    name: 'Administration',
    component: Administration
  },
  {
    path: '/team',
    name: 'Team',
    component: Team
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/tournament/:tournamentId',
    name: 'Tournament',
    component: Tournament,
    props: true
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: Notifications
  },
  {
    path: '/about',
    name: 'About',
    component: About
  }
]
const router = new VueRouter({
  routes
})

export default router
