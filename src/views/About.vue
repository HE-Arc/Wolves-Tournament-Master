<template>
  <div class="about">
    <h1>This is an about page</h1>
  </div>
</template>

<script>
import UserService from "@/services/UserService";

export default {
  data: () => ({
    users: []
  }),

  mounted() {
    this.GetUsers()
  },

  methods: {
    async GetUsers(){
      const response = await UserService.GetUsers()

      console.log(response)
    },
  }
}
</script>
