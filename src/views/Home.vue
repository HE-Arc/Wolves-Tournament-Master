<template>
  <div style="padding:30px;" class="home">
    <TournamentDialog ref="tournamentDialog" />
    <v-row>
      <v-col
        v-show="$store.state.isAuthenticated"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card
          @click="OpenTournamentDialog"
          style="padding:10px;"
        >
          <v-icon large>mdi-plus</v-icon>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="4">
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            src="https://www.youtube.com/embed/5LxzJ4rKQWw"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
          <v-card-title>FaZe vs. Astralis</v-card-title>
          <v-card-text>FINAL - IEM Sydney 2018</v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            src="https://www.youtube.com/embed/_Ef6cXH1oC8"
            allowfullscreen
          ></iframe>
          <v-card-title>Fnatic vs. EnVyUS</v-card-title>
          <v-card-text
            >FINAL - ESL One Cologne 2015</v-card-text
          >
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            src="https://www.youtube.com/embed/_Ef6cXH1oC8"
            allowfullscreen
          ></iframe>
          <v-card-title>Fnatic vs. EnVyUS</v-card-title>
          <v-card-text
            >FINAL - ESL One Cologne 2015</v-card-text
          >
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            src="https://www.youtube.com/embed/_Ef6cXH1oC8"
            allowfullscreen
          ></iframe>
          <v-card-title>Fnatic vs. EnVyUS</v-card-title>
          <v-card-text
            >FINAL - ESL One Cologne 2015</v-card-text
          >
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            src="https://www.youtube.com/embed/_Ef6cXH1oC8"
            allowfullscreen
          ></iframe>
          <v-card-title>Fnatic vs. EnVyUS</v-card-title>
          <v-card-text
            >FINAL - ESL One Cologne 2015</v-card-text
          >
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            src="https://www.youtube.com/embed/_Ef6cXH1oC8"
            allowfullscreen
          ></iframe>
          <v-card-title>Fnatic vs. EnVyUS</v-card-title>
          <v-card-text
            >FINAL - ESL One Cologne 2015</v-card-text
          >
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            src="https://www.youtube.com/embed/_Ef6cXH1oC8"
            allowfullscreen
          ></iframe>
          <v-card-title>Fnatic vs. EnVyUS</v-card-title>
          <v-card-text
            >FINAL - ESL One Cologne 2015</v-card-text
          >
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4">
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            src="https://www.youtube.com/embed/_Ef6cXH1oC8"
            allowfullscreen
          ></iframe>
          <v-card-title>Fnatic vs. EnVyUS</v-card-title>
          <v-card-text
            >FINAL - ESL One Cologne 2015</v-card-text
          >
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import TournamentDialog from '@/components/dialogs/TournamentDialog'

export default {
  name: 'Home',
  components: {
    TournamentDialog
  },
  methods: {
    async OpenTournamentDialog() {
      this.$refs.tournamentDialog.show()
    }
  }
}
</script>
