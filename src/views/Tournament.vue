<template>
  <div style="margin-top: 20px">
    <h1>ESL One 2018</h1>
    <div class="row">
      <div class="wrapper">
        <div class="item" id="match_1"></div>
      </div>
    </div>
  </div>
</template>

<script>
import TournamentCard from '../components/tournamentcard'

export default {
  //created() {
  mounted() {
    // todo add it only on creation
    this.generateEmptyMatches()
    this.setParents()
    this.setTeams()
    this.displayTree()
    //this.showMatches()
  },
  components: {
    // eslint-disable-next-line vue/no-unused-components
    TournamentCard
  },
  data: () => ({
    nbTeams: 8,
    //nbRounds: Math.log2(this.nbTeams),
    nbRounds: 3,
    matches: [],
    teams: [
      {
        id: 0,
        name: 'A'
      },
      {
        id: 1,
        name: 'B'
      },
      {
        id: 2,
        name: 'C'
      },
      {
        id: 3,
        name: 'D'
      },
      {
        id: 4,
        name: 'E'
      },
      {
        id: 5,
        name: 'F'
      },
      {
        id: 6,
        name: 'G'
      },
      {
        id: 7,
        name: 'H'
      }
    ]
  }),
  computed: {
    nbParents: function() {
      // Get the number of parent nodes (non-leaf nodes)
      let nbParents = 0
      for (
        let round = 0;
        round < this.nbRounds - 1;
        round++
      ) {
        nbParents += Math.pow(2, round)
      }
      return nbParents
    },
    nbMatches: function() {
      // returns the number of matches if it was a perfect binarytree
      return Math.pow(2, this.nbRounds) - 1
    }
  },
  methods: {
    /*
      ===================
        Tree
      ===================
    */

    generateEmptyMatches() {
      /*
        Generate tree with empty matches
      */
      //TODO get it from the db
      this.matches.push(null)

      //in binary trees, the first id is one
      for (let i = 0; i < this.nbMatches; i++) {
        this.matches.push({
          id: i + 1,
          idTeam1: 'unknow',
          idTeam2: 'unknow',
          idParent: null
        })
      }
    },
    setParents() {
      /*
        Set the parent for each node
      */
      for (
        let idParent = 1;
        idParent <= this.nbParents;
        idParent++
      ) {
        let firstChildId = 2 * idParent
        if (firstChildId <= this.nbMatches) {
          this.matches[firstChildId].idParent = idParent
        }

        if (firstChildId + 1 <= this.nbMatches) {
          this.matches[firstChildId + 1].idParent = idParent
        }
      }
    },
    setTeams() {
      /*
        Set teams into leafs (on an empty tournament)
      */
      let teamIndex = 0
      for (
        let i = this.nbParents + 1;
        i <= this.nbMatches;
        i++
      ) {
        this.matches[i].idTeam1 = this.teams[teamIndex++].id
        if (teamIndex < this.nbTeams) {
          this.matches[i].idTeam2 = this.teams[
            teamIndex++
          ].id
        }
      }
    },
    showMatches() {
      this.matches.forEach(element => {
        if (element != null && element.idParent != null) {
          console.log(
            'id : ' +
              element.id +
              ' team_name : ' +
              this.teams[element.id - 1].name +
              ', parent : ' +
              element.idParent +
              ' parent_name : ' +
              this.teams[element.idParent - 1].name +
              ', team1 : ' +
              element.idTeam1 +
              ', team2 : ' +
              element.idTeam2
          )
        } else {
          if (element != null) {
            console.log('id : ' + element.id)
          }
        }
      })
    },

    /*
      ===================
        Tree generation
      ===================
    */
    getTournamentCardString(
      idMatch,
      teamName,
      scoreMatch1,
      scoreMatch2
    ) {
      return (
        '<TournamentCard ' +
        ':idMatch="' +
        idMatch +
        '" ' +
        ':teamName="\'' +
        teamName +
        '\'" ' +
        ':scoreMatch1="\'' +
        scoreMatch1 +
        '\'" ' +
        ':scoreMatch2="\'' +
        scoreMatch2 +
        '\'" ' +
        '></TournamentCard>'
      )
    },
    getParentHTMLAsString(teamId) {
      return (
        '<div class="item-parent" id="\'' +
        teamId +
        '\'">' +
        this.getTournamentCardString(
          teamId,
          this.teams[teamId].name,
          '11-12',
          '11-16'
        ) +
        '</div>'
      )
    },
    getChildrenHTMLAsString(childId) {
      return (
        '<div class="item-childrens">' +
        '<div class="item-child">' +
        '<div class="item" id="' +
        childId +
        '">' +
        '</div>' +
        '</div>' +
        '</div>'
      )
    },
    createChildrenDOMNode(childId) {
      return this.createDOMNodeFromHTML(
        this.getChildrenHTMLAsString(childId)
      )
    },
    createParentDOMNode(
      id
      //child1Id
      //child2Id
    ) {
      let node = this.createDOMNodeFromHTML(
        this.getParentHTMLAsString(id)
      )
      // let child1Node = this.createDOMNodeFromHTML(
      //   this.getChildrenHTMLAsString(child1Id)
      // )

      // node.append(child1Node)

      return node
      //(child2Id != -1)
      //? this.getChildrenHTMLAsString(child2Id)
      //: ''
    },
    createDOMNodeFromHTML(htmlString) {
      /*
        create an HTML node from HTML string
      */
      var div = document.createElement('div')
      div.innerHTML = htmlString //.trim()

      // Change this to div.childNodes to support multiple top-level nodes
      return div.firstChild
    },
    displayTree() {
      /*
        Set the parent for each node
      */
      for (
        let idMatch = 1;
        idMatch <= this.matches.length;
        idMatch++
      ) {
        /*
          Note : each item contains its parent node

          for each parents :
            - search the corresponding item with its id
            - create a parent div and insert its data into it (add a tournament card into it)
                - add this parent div in the item
            - Create a children-items div
              - into this div, create a child div and an item div for each children
              - the item div will have the id of the child

          if the item is not a parent :
            - just create a child-item div and add its tournament card into it
        */

        let firstChildId = 2 * idMatch
        let idChild1 = -1
        //let idChild2 = -1

        if (firstChildId <= this.nbMatches) {
          idChild1 = firstChildId
        }

        if (firstChildId + 1 <= this.nbMatches) {
          //idChild2 = firstChildId
        }

        if (idChild1 != -1) {
          console.log(idMatch)
          // it's a parent
          let item = document.getElementById(
            'match_' + idMatch
          )
          item.appendChild(
            this.createParentDOMNode(idMatch)
          )
          item.appendChild(
            this.createChildrenDOMNode(idChild1)
          )

          // idChild2
        } else {
          //just create a child-item div and add its tournament card into it
        }
      }
    }
  }
}
</script>

<style lang="scss">
$side-margin: 50px;
$vertical-margin: 10px;
$line-color: black;

.wrapper {
  display: flex;
  height: auto;
  width: 100%;
  justify-content: center;
}

.item {
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
