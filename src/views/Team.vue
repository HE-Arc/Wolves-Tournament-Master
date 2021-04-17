<template>
  <v-container style="margin-top:30px;">
    <TeamDialog ref="teamDialog" />
    <RecruitDialog ref="recruitDialog" />

    <v-row>
      <v-slide-group style="margin-left:10px;" multiple show-arrows xs="12">
        <v-slide-item>
          <v-btn
            color="#01002a"
            outlined
            class="mx-2"
            tile
            large
            @click="CreateTeam"
          >
            + Create team
          </v-btn>
        </v-slide-item>
        <v-slide-item v-for="team in teams" :key="team.name">
          <v-btn class="mx-2" tile dark large @click="SelectTeam(team)">
            {{ team.name }}
          </v-btn>
        </v-slide-item>
      </v-slide-group>
    </v-row>
    <v-row>
      <v-divider> </v-divider>
    </v-row>

    <div v-show="!selectedTeam" style="margin-top:30px;">
      <v-alert outlined type="info">
        For now, you are not part of any team
      </v-alert>
    </div>
    <div v-show="selectedTeam" style="margin-top:30px;">
      <v-card v-show="selectedTeam" style="margin-bottom:30px;" tile>
        <v-row
          style="margin:0;padding-left:16px;padding-right:16px"
          v-show="selectedTeam"
          align="center"
        >
          <img width="80px" height="auto" src="@/assets/logo.png" alt="logo" />
          <h1 style="color:#01002a;margin-left:10px;" class="text-xs-left">
            {{ this.selectedTeam.name }}
          </h1>
          <v-spacer></v-spacer>
          <v-btn
            v-if="selectedTeam.leader == $store.state.authUser.name"
            tile
            dark
            large
            @click="Recruit"
          >
            Recruit a new member
          </v-btn>
        </v-row>
      </v-card>
      <v-row>
        <v-col xs="12" md="4">
          <v-card tile>
            <v-card-title color="#01002a">Awards</v-card-title>
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
            <v-card-title color="#01002a">Members</v-card-title>
            <v-list three-line>
              <template>
                <v-list-item v-for="member in members" :key="member.id">
                  <v-list-item-avatar>
                    <v-icon
                      v-if="member.username == selectedTeam.leader"
                      class="grey lighten-1"
                      dark
                    >
                      mdi-account-star
                    </v-icon>
                    <v-icon v-else class="grey lighten-1" dark>
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
                      selectedTeam.leader == $store.state.authUser.name &&
                        selectedTeam.leader != member.username
                    "
                    tile
                    color="#01002a"
                    outlined
                    @click="DeleteTeamMember(selectedTeam, member)"
                    >Exclude</v-btn
                  >
                </v-list-item>
              </template>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script>
import WtmApi from '@/services/WtmApiService'
import RecruitDialog from '@/components/dialogs/RecruitDialog'
import TeamDialog from '@/components/dialogs/TeamDialog'

export default {
  components: {
    RecruitDialog,
    TeamDialog
  },
  metaInfo: {
    title: 'Team'
  },
  data: () => ({
    teams: [],
    members: [],
    selectedTeam: false,
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
        items: [{ title: '3rd - LCS' }],
        title: 'LoL'
      }
    ]
  }),
  mounted: function() {
    this.GetTeams()
  },
  methods: {
    // Open the team dialog
    async CreateTeam() {
      this.$refs.teamDialog.show(this, 'Add a new team', null, false)
    },

    // Open the recruit dialog
    async Recruit() {
      this.$refs.recruitDialog.show()
      this.$refs.recruitDialog.team = this.selectedTeam
      this.$refs.recruitDialog.teamMembers = this.members
    },

    // Get current authenticated user's teams
    async GetTeams() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'teams/' +
          this.$store.state.authUser.id +
          '/getteamsbymember/',
        null,
        this.$store.getters.getAxiosHeader
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

    /**
     * Select the team to show
     *
     * @param {Object} team team to show
     */
    SelectTeam(team) {
      this.GetTeamMembers(team)
      this.selectedTeam = team
    },

    /**
     * Get current team's members
     *
     * @param {Object} team current team
     */
    async GetTeamMembers(team) {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl + 'users/' + team.id + '/getteammembers/',
        null,
        this.$store.getters.getAxiosHeader
      )
      if (response.isSuccess) {
        this.members = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.loading = false
    },

    /**
     * Dellete user of team's members list
     *
     * @param {Object} team current team
     * @param {Object} member user to delete
     */
    async DeleteTeamMember(team, member) {
      let data = {
        userid: member.id
      }
      const response = await WtmApi.Request(
        'post',
        this.$store.state.apiUrl + 'teams/' + team.id + '/removeuser/',
        data,
        this.$store.getters.getAxiosHeader
      )
      if (response.isSuccess) {
        this.GetTeamMembers(team)
        this.$snotify.success('User removed!')
      } else {
        this.$snotify.error('Unable to remove user...')
      }
    }
  }
}
</script>
