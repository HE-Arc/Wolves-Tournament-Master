<template>
  <v-app>
    <vue-snotify></vue-snotify>
    <Navigation />
    <AppBar />

    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import Navigation from '@/components/Navigation'
import AppBar from '@/components/AppBar'

export default {
  name: 'App',

  metaInfo: {
    title: 'Home',
    titleTemplate: '%s - WTM',
    htmlAttrs: {
      lang: 'en',
      amp: true
    }
  },

  components: {
    Navigation,
    AppBar
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
