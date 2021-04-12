<template>
  <div style="margin:30px;">
    <v-row>
      <v-slide-group multiple show-arrows xs="12">
        <v-slide-item
          v-for="team in teams"
          :key="team.name"
          v-slot="{ active }"
        >
          <v-btn
            class="mx-2"
            :input-value="active"
            active-class="purple white--text"
            @click="SelectTeam(team)"
          >
            {{ team.name }}
          </v-btn>
        </v-slide-item>
        <v-slide-item v-if="teams.length == 0">
          <v-btn
            class="mx-2"
            :input-value="active"
            active-class="purple white--text"
            @click="SelectTeam(team)"
          >
            + Créer une équipe
          </v-btn>
        </v-slide-item>
      </v-slide-group>
    </v-row>
    <v-row>
      <v-divider> </v-divider>
    </v-row>
    <v-row align="center">
      <img
        width="80px"
        height="auto"
        src="@/assets/logo.png"
        alt="logo"
      />
      <h1 style="margin-left:10px;" class="text-xs-left">
        {{ this.selectedTeam.name }}
      </h1>
      <v-spacer></v-spacer>
      <v-btn color="#01002a" tile dark large
        >Recruter un nouveau membre</v-btn
      >
    </v-row>
    <v-row>
      <v-col xs="12" md="4">
        <v-card tile>
          <v-card-title color="#01002a"
            >Palmarès</v-card-title
          >
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

              <v-list-item
                v-for="child in item.items"
                :key="child.title"
              >
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
          <v-card-title color="#01002a"
            >Membres</v-card-title
          >
          <v-list three-line>
            <template>
              <v-list-item
                v-for="member in members"
                :key="member.id"
              >
                <v-list-item-avatar>
                  <v-icon
                    v-if="
                      member.username == selectedTeam.leader
                    "
                    class="grey lighten-1"
                    dark
                  >
                    mdi-account-star
                  </v-icon>
                  <v-icon
                    v-else
                    class="grey lighten-1"
                    dark
                  >
                    mdi-account
                  </v-icon>
                </v-list-item-avatar>

                <v-list-item-content>
                  <v-list-item-title
                    class="text-sm-left"
                    v-html="member.username"
                  ></v-list-item-title>
                  <v-list-item-subtitle
                    class="text-sm-left"
                    v-html="member.email"
                  ></v-list-item-subtitle>
                </v-list-item-content>
                <v-btn
                  v-if="
                    selectedTeam.leader ==
                      $store.state.authUser.name &&
                      selectedTeam.leader != member.username
                  "
                  tile
                  outlined
                  color="#01002a"
                  >Virer</v-btn
                >
              </v-list-item>
            </template>
            <!-- <template v-for="(item, index) in members">
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
                    v-html="item.username"
                  ></v-list-item-title>
                  <v-list-item-subtitle
                    class="text-sm-left"
                    v-html="item.email"
                  ></v-list-item-subtitle>
                </v-list-item-content>
                <v-btn tile outlined color="#01002a"
                  >Virer</v-btn
                >
              </v-list-item>
            </template> -->
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import WtmApi from '@/services/WtmApiService'

export default {
  components: {},

  data: () => ({
    teams: [],
    members: [],
    selectedTeam: 0,
    items: [
      {
        action: 'mdi-ticket',
        items: [
          { title: '1er - ESL One 2018' },
          { title: '1er - ESL One 2019' },
          { title: '2ème - ESL One 2020' }
        ],
        title: 'CS : GO'
      },
      {
        action: 'mdi-trophy-variant',
        active: true,
        items: [{ title: '3ème - LCS' }],
        title: 'LoL'
      }
    ]
    // players: [
    //   {
    //     avatar:
    //       'https://cdn.vuetifyjs.com/images/lists/1.jpg',
    //     title: 'Ali Connors',
    //     subtitle: 'CS:GO, LoL'
    //   },
    //   { divider: true, inset: true },
    //   {
    //     avatar:
    //       'https://cdn.vuetifyjs.com/images/lists/2.jpg',
    //     title: 'Alex Scott',
    //     subtitle: 'CS:GO'
    //   },
    //   { divider: true, inset: true },
    //   {
    //     avatar:
    //       'https://cdn.vuetifyjs.com/images/lists/3.jpg',
    //     title: 'Sandra Adams',
    //     subtitle: 'CS:GO, LoL'
    //   },
    //   { divider: true, inset: true },
    //   {
    //     avatar:
    //       'https://cdn.vuetifyjs.com/images/lists/4.jpg',
    //     title: 'Trevor Hanse',
    //     subtitle: 'LoL'
    //   },
    //   { divider: true, inset: true },
    //   {
    //     avatar:
    //       'https://cdn.vuetifyjs.com/images/lists/5.jpg',
    //     title: 'Britta Holt',
    //     subtitle: 'CS:GO'
    //   }
    // ]
  }),
  mounted: function() {
    this.GetTeamsByMember()
  },
  methods: {
    async GetTeamById() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'teams/' +
          this.$store.state.authUser.team +
          '/',
        null,
        this.$store.getters.getAxiosConfig
      )

      if (response.isSuccess) {
        this.teams = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.loading = false
    },
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
        if (this.teams.length > 0) {
          this.SelectTeam(this.teams[0])
        }
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.loading = false
    },
    SelectTeam(team) {
      this.GetTeamMembers(team)
      this.selectedTeam = team
      console.log('leader = ' + team.leader)
    },
    async GetTeamMembers(team) {
      this.loading = true
      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'users/' +
          team.id +
          '/getteammembers/',
        null,
        this.$store.getters.getAxiosConfig
      )
      if (response.isSuccess) {
        this.members = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.loading = false
    }
  }
}
</script>
