<template>
  <v-dialog v-model="isVisible" max-width="500px" @keydown.esc="hide">
    <v-card>
      <v-toolbar dark color="#01002a">
        <v-toolbar-title>{{ title }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn icon dark @click="hide">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-title></v-card-title>
      <v-card-text>
        <v-form ref="form" style="padding:10px;">
          <v-text-field
            v-model="name"
            label="Name"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="Name"
            :error-messages="errors.collect('Name')"
          ></v-text-field>
          <v-text-field
            v-model="leader"
            label="Leader"
            outlined
            dense
            clearable
            v-validate="'required'"
            data-vv-name="Leader"
            :error-messages="errors.collect('Leader')"
          ></v-text-field>
          <v-alert
            v-show="error"
            v-model="error"
            dismissible
            outlined
            type="error"
          >
            An error occured... Please try later!
          </v-alert>
        </v-form>
      </v-card-text>
      <v-card-actions v-show="!loading">
        <v-spacer></v-spacer>
        <v-btn v-show="!isUpdate" tile color="success" @click="CreateTeam">
          Save
          <v-icon right> mdi-content-save </v-icon>
        </v-btn>
        <v-btn v-show="isUpdate" tile color="success" @click="UpdateTeam">
          Save
          <v-icon right> mdi-content-save </v-icon>
        </v-btn>
      </v-card-actions>
      <v-card-actions v-show="loading">
        <v-spacer></v-spacer>
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import TeamService from "@/services/TeamService";

export default {
  data: () => ({
    isVisible: false,
    parent: undefined,
    title: "",
    item: [],
    isUpdate: false,
    loading: false,
    error: false,

    id: null,
    name: "",
    leader: ""
  }),

  mounted() {},

  methods: {
    // To show the dialog
    show(parent, title, item, isUpdate) {
      this.parent = parent;
      this.title = title;
      this.item = item;
      this.isUpdate = isUpdate;

      if (isUpdate) {
        this.name = item.name;
        this.leader = item.leader;
      }

      this.isVisible = true;
    },
    hide() {
      this.$refs.form.reset();
      this.isVisible = false;
    },
    async CreateTeam() {
      const result = await this.$validator.validate();

      if (result) {
        this.loading = true;

        let team = {
          name: this.name,
          leader: this.leader
        };

        const result = await TeamService.CreateTeam(team);

        if (result) {
          this.$refs.form.reset();
          this.$snotify.success(team.name + " added successfuly!");
          this.isVisible = false;
          this.parent.GetTeams();
        } else {
          this.$snotify.error(
            "Unable to save this team...\nPlease try later..."
          );
          this.error = true;
        }

        this.loading = false;
      }
    },
    async UpdateTeam() {
      const result = await this.$validator.validate();

      if (result) {
        this.loading = true;

        this.item.name = this.name;
        this.item.leader = this.leader;

        const result = await TeamService.UpdateTeam(this.$store.state.token, this.item);

        if (result.id) {
          this.$refs.form.reset();
          this.$snotify.success(this.item.name + " updated successfuly!");
          this.isVisible = false;
          this.parent.GetTeams();
        } else {
          this.$snotify.error(
            "Unable to update this formation...\nPlease try later..."
          );
          this.error = true;
        }

        this.loading = false;
      }
    }
  }
};
</script>
