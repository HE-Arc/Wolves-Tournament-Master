<template>
  <div style="margin:30px;">
    <div v-show="!selectedTeam">
      <v-alert outlined type="info">
        For now, you are not part of any team
      </v-alert>
    </div>
    <div v-show="selectedTeam">
      <v-row>
        <v-slide-group multiple show-arrows xs="12">
          <v-slide-item
            v-for="team in teams"
            :key="team.name"
            v-slot="{ active }"
          >
            <v-btn
              color="#01002a"
              tile
              dark
              large
              class="mx-2"
              :input-value="active"
              active-class="purple white--text"
              @click="SelectTeam(team)"
            >
              {{ team.name }}
            </v-btn>
          </v-slide-item>
        </v-slide-group>
      </v-row>
      <v-row>
        <v-divider> </v-divider>
      </v-row>
      <v-row align="center">
        <img width="80px" height="auto" src="@/assets/logo.png" alt="logo" />
        <h1 style="margin-left:10px;" class="text-xs-left">
          {{ this.selectedTeam.name }}
        </h1>
        <v-spacer></v-spacer>
        <v-btn color="#01002a" outlined tile dark large
          >Recruit a new member</v-btn
        >
      </v-row>
      <v-row>
        <v-col xs="12" md="4">
          <v-card tile>
            <v-card-title>
              <v-icon style="margin-right:20px;">mdi-trophy-variant</v-icon>
              Prize list
            </v-card-title>
            <v-list>
              <v-list-group
                v-for="item in items"
                :key="item.title"
                v-model="item.active"
                :prepend-icon="item.action"
                no-action
              >
                <template v-slot:activator>
                  <v-list-item-content>
                    <v-list-item-title
                      class="text-sm-left"
                      v-text="item.title"
                    ></v-list-item-title>
                  </v-list-item-content>
                </template>

                <v-list-item v-for="child in item.items" :key="child.title">
                  <v-list-item-content>
                    <v-list-item-title
                      class="text-sm-left"
                      v-text="child.title"
                    ></v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-group>
            </v-list>
          </v-card>
        </v-col>
        <v-col xs="12" md="8">
          <v-card tile>
            <v-card-title>
              <v-icon style="margin-right:20px;">mdi-account-multiple</v-icon>
              Members
            </v-card-title>
            <v-list three-line>
              <template v-for="(item, index) in players">
                <v-divider
                  v-if="item.divider"
                  :key="index"
                  :inset="item.inset"
                ></v-divider>

                <v-list-item v-else :key="item.title">
                  <v-list-item-avatar>
                    <v-img :src="item.avatar"></v-img>
                  </v-list-item-avatar>

                  <v-list-item-content>
                    <v-list-item-title
                      class="text-sm-left"
                      v-html="item.title"
                    ></v-list-item-title>
                    <v-list-item-subtitle
                      class="text-sm-left"
                      v-html="item.subtitle"
                    ></v-list-item-subtitle>
                  </v-list-item-content>
                  <v-btn tile outlined color="#01002a">Fired</v-btn>
                </v-list-item>
              </template>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
import WtmApi from '@/services/WtmApiService'

export default {
  components: {},
  metaInfo: {
    title: 'Team'
  },
  data: () => ({
    teams: [],
    selectedTeam: false,
    teamMembers: [],
    items: [
      {
        action: 'mdi-gamepad-variant',
        items: [
          { title: '1st - ESL One 2018' },
          { title: '1st - ESL One 2019' },
          { title: '2nd - ESL One 2020' }
        ],
        title: 'CS : GO'
      },
      {
        action: 'mdi-gamepad-variant',
        active: true,
        items: [{ title: '3rd - LCS' }],
        title: 'LoL'
      }
    ],
    players: [
      {
        avatar: 'https://cdn.vuetifyjs.com/images/lists/1.jpg',
        title: 'Ali Connors',
        subtitle: 'CS:GO, LoL'
      },
      { divider: true, inset: true },
      {
        avatar: 'https://cdn.vuetifyjs.com/images/lists/2.jpg',
        title: 'Alex Scott',
        subtitle: 'CS:GO'
      },
      { divider: true, inset: true },
      {
        avatar: 'https://cdn.vuetifyjs.com/images/lists/3.jpg',
        title: 'Sandra Adams',
        subtitle: 'CS:GO, LoL'
      },
      { divider: true, inset: true },
      {
        avatar: 'https://cdn.vuetifyjs.com/images/lists/4.jpg',
        title: 'Trevor Hanse',
        subtitle: 'LoL'
      },
      { divider: true, inset: true },
      {
        avatar: 'https://cdn.vuetifyjs.com/images/lists/5.jpg',
        title: 'Britta Holt',
        subtitle: 'CS:GO'
      }
    ]
  }),
  mounted: function() {
    this.GetTeamsByMember()
  },
  methods: {
    async GetTeamsByMember() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'teams/' +
          this.$store.state.authUser.id +
          '/getteamsbymember/',
        null,
        this.$store.getters.getAxiosConfig
      )

      if (response.isSuccess) {
        this.teams = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.teams.length > 0
        ? this.SelectTeam(this.teams[0])
        : (this.selectedTeam = false)

      this.loading = false
    },
    SelectTeam(team) {
      this.GetTeamMembers(team)
      this.selectedTeam = team
    },
    async GetTeamMembers(team) {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl + 'users/' + team.id + '/getteammembers/',
        null,
        this.$store.getters.getAxiosConfig
      )
      if (response.isSuccess) {
        this.teamMembers = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.loading = false
    }
  }
}
</script>
