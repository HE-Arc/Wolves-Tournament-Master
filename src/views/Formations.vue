<template>
  <div class="formations">
    <FormationDialog ref="formationDialog" />
	<DeleteModal ref="deleteFormation" :action="DeleteFormation" />

	<v-layout style="margin:20px;"> 
		<v-flex xs12>	
			<v-alert class="text-xs-center" v-show="loading" outlined v-model="loading" type="info">
				<v-progress-circular indeterminate color="primary"></v-progress-circular>
			</v-alert>
			<template>
				<v-data-table
					v-show="!loading"
					:headers="headers"
					:items="formations"
					sort-by="calories"
					class="elevation-1"
				>
					<template v-slot:top>
						<v-toolbar flat>
							<v-toolbar-title>FORMATIONS</v-toolbar-title>
							<v-divider
							class="mx-4"
							inset
							vertical
							></v-divider>
							<v-spacer></v-spacer>
							<v-btn
								@click.stop="CreateFormation"
								color="primary"
								dark
								class="mb-2"
							>
								New Item
							</v-btn>
						</v-toolbar>
					</template>
					<template v-slot:[`item.actions`]="{ item }">
						<v-icon
							small
							class="mr-2"
							@click="UpdateFormation(item)"
						>
							mdi-pencil
						</v-icon>
						<v-icon
							small
							@click="OpenDeleteModal(item)"
						>
							mdi-delete
					</v-icon>
					</template>
				</v-data-table>
			</template>
		</v-flex>	  
	</v-layout>
    
  </div>
</template>

<script>
import FormationService from "@/services/FormationService"
import FormationDialog from "@/components/dialogs/Formation"
import DeleteModal from "@/components/modals/Delete"

export default {
	components: {
		FormationDialog,
		DeleteModal
	},

	data: () => ({
		formations: [
			{
				id: 1,
				name: "Security",
				validity: 6,
				points: 30,
				managerName: "George"
			}
		],
		loading: false,
		headers: [
			{text: "ID", value:"id"},
			{text: "Name", value:"name"},
			{text: "Validity", value:"validity"},
			{text: "Points", value:"points"},
			{text: "Manager name", value:"managerName"},
			{text: "Actions", value:"actions", sortable:false}
		],
		showFormationDialog: false,
	}),
	mounted: function(){
		this.GetFormations();
	},
	methods: {
		async CreateFormation(){
			this.$refs.formationDialog.show(this, "Add a new formation", null, false)
		},
		async UpdateFormation(formation){
			this.$refs.formationDialog.show(this, "Update formation", formation, true)
		},
		async GetFormations(){
			this.loading = true
			let response = await FormationService.GetFormations()

			if(response.isSuccess){
				this.formations = response.result	
			}
			else {
				this.$snotify.error("Unable to get formations...")
			}

			this.loading = false
		},
		async OpenDeleteModal(formation) {
			this.$refs.deleteFormation.show(formation)
		},
		async DeleteFormation(formation) {
			let response = await FormationService.DeleteFormation(formation)

			if(response.isSuccess) {
				this.$snotify.success("Formation '" + formation.name + "' deleted successfuly")
				this.$refs.deleteFormation.hide()
				this.GetFormations()
			}
			else {
				this.$snotify.error("Unable to delete this formation...")
				this.$refs.deleteFormation.loading = false
				this.$refs.deleteFormation.hide()
			}
		}
	}
};
</script>
