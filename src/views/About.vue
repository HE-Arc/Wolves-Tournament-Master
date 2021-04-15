<template>
  <v-col xs="12" offset-sm="3" sm="6" offset-md="4" md="4">
    <v-card class="text-left">
      <v-card-title>About</v-card-title>
      <v-card-text>
        <img
          style="margin-top:10px;"
          height="50px"
          width="166px"
          src="@/assets/arc-logo.png"
        />
        <p>
          This project has been realized as part of the school "Haute Ecole Arc
          (HE-Arc) BEJUNE" during the course "Développement web".
        </p>
        <p>Contributors :</p>
        <ul>
          <li>Alan Chambaz</li>
          <li>Colin Pelletier</li>
          <li>Sébastien Roso</li>
        </ul>
      </v-card-text>
    </v-card>
  </v-col>
</template>

<script>
export default {
  metaInfo: {
    title: 'About'
  },
  data: () => ({
    users: []
  }),

  mounted() {},

  methods: {}
}
</script>
