import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Teams from '../views/Teams.vue'
import Team from '../views/Team.vue'
import Register from '../views/Register.vue'
import Tournament from '../views/Tournament.vue'
import Notifications from "../views/Notifications.vue";

Vue.use(VueRouter)

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/teams',
        name: 'Teams',
        component: Teams
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
        path: '/tournament',
        name: 'Tournament',
        component: Tournament
    },
    {
        path: '/about',
        name: 'About',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
    }
]

  {
    path: "/notifications",
    name: "Notifications",
    component: Notifications,
  },
const router = new VueRouter({
    routes
})

export default router
