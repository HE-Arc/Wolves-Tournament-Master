<template>
  <v-dialog v-model="isVisible" max-width="500px" @keydown.esc="hide">
    <v-card>
      <v-toolbar dark color="primary">
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
            v-model="validity"
            label="Validity period"
            outlined
            dense
            clearable
            v-validate="'required|numeric'"
            data-vv-name="Validity"
            :error-messages="errors.collect('Validity')"
          ></v-text-field>
          <v-text-field
            v-model="points"
            label="Total of points"
            outlined
            dense
            clearable
            v-validate="'required|numeric'"
            data-vv-name="Points"
            :error-messages="errors.collect('Points')"
          ></v-text-field>
          <v-text-field
            v-model="managerName"
            label="Manager's name"
            outlined
            dense
            clearable
            v-validate="'required'"
            data-vv-name="Manager"
            :error-messages="errors.collect('Manager')"
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
        <v-btn v-show="!isUpdate" tile color="success" @click="CreateFormation">
          Save
          <v-icon right> mdi-content-save </v-icon>
        </v-btn>
        <v-btn v-show="isUpdate" tile color="success" @click="UpdateFormation">
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
import FormationService from "@/services/FormationService";

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
    validity: "",
    points: "",
    managerName: ""
  }),

  mounted() {},

  methods: {
    // To show the dialog
    show(parent, title, item, isUpdate) {
      this.parent = parent
      this.title = title
      this.item = item
      this.isUpdate = isUpdate

      if(isUpdate) {
        this.name = item.name
        this.validity = item.validity
        this.points = item.points
        this.managerName = item.managerName
      }

      this.isVisible = true
    },
    hide() {
      this.$refs.form.reset()
      this.isVisible = false
    },
    async CreateFormation() {
      const result = await this.$validator.validate()

      if(result) {
        this.loading = true

        let formation = {
          name: this.name,
          validity: this.validity,
          points: this.points,
          managerName: this.managerName
        }

        const response = await FormationService.CreateFormation(formation)

        if(response.isSuccess) {
          this.$refs.form.reset()
          this.$snotify.success(formation.name + ' added successfuly!')
          this.isVisible = false
          this.parent.GetFormations()
        }
        else {
          this.$snotify.error('Unable to save this formation...\nPlease try later...')
          this.error = true
        }

        this.loading = false
      }
    },
    async UpdateFormation() {
      const result = await this.$validator.validate()

      if(result) {
        this.loading = true

        this.item.name = this.name
        this.item.validity = this.validity
        this.item.points = this.points
        this.item.manageName = this.managerName

        const response = await FormationService.UpdateFormation(this.item)

        if(response.isSuccess) {
          this.$refs.form.reset()
          this.$snotify.success(this.item.name + ' updated successfuly!')
          this.isVisible = false
          this.parent.GetFormations()
        }
        else {
          this.$snotify.error('Unable to update this formation...\nPlease try later...')
          this.error = true
        }

        this.loading = false
      }
    }
  }
};
</script>