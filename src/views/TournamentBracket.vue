<template>
  <Bracket :rounds="rounds">
    <template slot="player" slot-scope="player">
      {{ player.name }}
    </template>
  </Bracket>
</template>

<script>
import Bracket from 'vue-tournament-bracket'

export default {
  components: {
    Bracket
  },
  data() {
    return {
      rounds: rounds
    }
  }
}

const rounds = [
  //quarter finals
  {
    games: [
      {
        player1: {
          id: '1',
          name: 'Competitor 1',
          winner: false
        },
        player2: {
          id: '4',
          name: 'Competitor 4',
          winner: true
        }
      },
      {
        player1: {
          id: '5',
          name: 'Competitor 5',
          winner: false
        },
        player2: {
          id: '8',
          name: 'Competitor 8',
          winner: true
        }
      },
      {
        player1: {
          id: '5',
          name: 'Competitor 5',
          winner: false
        },
        player2: {
          id: '8',
          name: 'Competitor 8',
          winner: true
        }
      },
      {
        player1: {
          id: '5',
          name: 'Competitor 5',
          winner: false
        },
        player2: {
          id: '8',
          name: 'Competitor 8',
          winner: true
        }
      }
    ]
  },
  //Semi finals
  {
    games: [
      {
        player1: {
          id: '1',
          name: 'Competitor 1',
          winner: false
        },
        player2: {
          id: '4',
          name: 'Competitor 4',
          winner: true
        }
      },
      {
        player1: {
          id: '5',
          name: 'Competitor 5',
          winner: false
        },
        player2: {
          id: '8',
          name: 'Competitor 8',
          winner: true
        }
      }
    ]
  },
  //Final
  {
    games: [
      {
        player1: {
          id: '4',
          name: 'Competitor 4',
          winner: false
        },
        player2: {
          id: '8',
          name: 'Competitor 8',
          winner: true
        }
      }
    ]
  }
]
</script>

<style lang="scss">
$side-margin: 50px;
$vertical-margin: 10px;
$line-color: black;

.vtb-wrapper {
  display: flex;
  height: auto;
  width: 100%;
  justify-content: center;
}

.vtb-item {
  display: flex;
  flex-direction: row-reverse;

  &-parent {
    position: relative;
    margin-left: $side-margin;
    display: flex;
    align-items: center;
    &:after {
      position: absolute;
      content: '';
      width: $side-margin/2;
      height: 2px;
      left: 0;
      top: 50%;
      background-color: $line-color;
      transform: translateX(-100%);
    }
  }
  &-childrens {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  &-child {
    display: flex;
    align-items: flex-start;
    justify-content: flex-end;
    margin-top: $vertical-margin;
    margin-bottom: $vertical-margin;
    position: relative;
    &:before {
      content: '';
      position: absolute;
      background-color: $line-color;
      right: 0;
      top: 50%;
      transform: translateX(100%);
      width: 25px;
      height: 2px;
    }
    &:after {
      content: '';
      position: absolute;
      background-color: $line-color;
      right: -$side-margin / 2;
      height: calc(50% + 22px);
      width: 2px;
      top: 50%;
    }
    &:last-child {
      &:after {
        transform: translateY(-100%);
      }
    }
    &:only-child:after {
      display: none;
    }
  }
}
</style>
