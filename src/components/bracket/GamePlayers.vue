<template>
  <div class="vtb-item-players">
    <MatchResultDialog ref="matchResultDialog" />
    <div>
      <v-card tile>
        <v-expansion-panels>
          <v-expansion-panel>
            <v-expansion-panel-header>
              <div
                :class="[
                  'vtb-player',
                  'vtb-player1',
                  getPlayerClass(bracketNode.player1)
                ]"
                @mouseover="highlightPlayer(bracketNode.player1.id)"
                @mouseleave="unhighlightPlayer"
              >
                <slot :player="bracketNode.player1" name="player" />
              </div>
              <p>VS</p>
              <div
                :class="[
                  'vtb-player',
                  'vtb-player2',
                  getPlayerClass(bracketNode.player2)
                ]"
                @mouseover="highlightPlayer(bracketNode.player2.id)"
                @mouseleave="unhighlightPlayer"
              >
                <slot :player="bracketNode.player2" name="player" />
              </div>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <p>
                Score : {{ bracketNode.match.score1 }} -
                {{ bracketNode.match.score2 }}
              </p>
              <v-btn tile outlined @click="OpenMatchResultDialog(bracketNode)"
                >Ajouter un résultat</v-btn
              >
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card>
    </div>
    <slot name="player-extension-bottom" :match="matchProperties" />
  </div>
</template>

<script>
import MatchResultDialog from '@/components/dialogs/MatchResultDialog'

export default {
  name: 'game-players',
  props: ['bracketNode', 'highlightedPlayerId'],
  components: {
    MatchResultDialog
  },
  computed: {
    matchProperties() {
      return Object.assign({}, this.bracketNode, {
        games: undefined,
        hasParent: undefined
      })
    }
  },
  methods: {
    getPlayerClass(player) {
      if (player.winner === null || player.winner === undefined) {
        return ''
      }

      let clazz = player.winner ? 'winner' : 'defeated'

      if (this.highlightedPlayerId === player.id) {
        clazz += ' highlight'
      }

      return clazz
    },
    highlightPlayer(playerId) {
      this.$emit('onSelectedPlayer', playerId)
    },
    unhighlightPlayer() {
      this.$emit('onDeselectedPlayer')
    },
    async OpenMatchResultDialog(bracketNode) {
      this.$refs.matchResultDialog.show(bracketNode)
    }
  }
}
</script>
