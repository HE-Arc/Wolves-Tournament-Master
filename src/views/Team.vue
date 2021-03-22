<template>
  <div style="margin:30px;">
    <v-row align="center">
      <img
        width="80px"
        height="auto"
        src="@/assets/logo.png"
        alt="logo"
      />
      <h1 style="margin-left:10px;" class="text-xs-left">
        Faze Clan
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
                <v-btn tile outlined color="#01002a"
                  >Virer</v-btn
                >
              </v-list-item>
            </template>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import TeamService from '@/services/TeamService'

export default {
  components: {},

  data: () => ({
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
        action: 'mdi-silverware-fork-knife',
        active: true,
        items: [{ title: '3ème - LCS' }],
        title: 'LoL'
      }
    ],
    players: [
      {
        avatar:
          'https://cdn.vuetifyjs.com/images/lists/1.jpg',
        title: 'Ali Connors',
        subtitle: 'CS:GO, LoL'
      },
      { divider: true, inset: true },
      {
        avatar:
          'https://cdn.vuetifyjs.com/images/lists/2.jpg',
        title: 'Alex Scott',
        subtitle: 'CS:GO'
      },
      { divider: true, inset: true },
      {
        avatar:
          'https://cdn.vuetifyjs.com/images/lists/3.jpg',
        title: 'Sandra Adams',
        subtitle: 'CS:GO, LoL'
      },
      { divider: true, inset: true },
      {
        avatar:
          'https://cdn.vuetifyjs.com/images/lists/4.jpg',
        title: 'Trevor Hanse',
        subtitle: 'LoL'
      },
      { divider: true, inset: true },
      {
        avatar:
          'https://cdn.vuetifyjs.com/images/lists/5.jpg',
        title: 'Britta Holt',
        subtitle: 'CS:GO'
      }
    ]
  }),
  mounted: function() {
    this.GetTeamById()
  },
  methods: {
    async GetTeamById() {
      this.loading = true

      let response = await TeamService.GetTeamById(
        this.$store.state.authUser.team
      )

      if (response.isSuccess) {
        this.teams = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.loading = false
    }
  }
}
</script>
