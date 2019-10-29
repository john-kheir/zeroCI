<template>
  <ul class="nav">
    <li style="color: #fff;padding: 15px;">
      <i class="lnr lnr-book"></i>
      <span>Repos</span>
    </li>
    <li v-for="(repo, index) in repos" :key="index">
      <router-link
        :to="{ name: 'Repos', params: { name: repo }}"
      >{{ repo.substring(repo.indexOf("/") + 1) }}</router-link>
    </li>
  </ul>
</template>

<script>
import axios from "axios";
export default {
  name: "ItemsWithDropdown",
  data() {
    return {
      repos: null
    };
  },
  methods: {
    getRepos() {
      this.Repos = this.getData();
    },
    getData() {
      const path = `https://zeroci.grid.tf/api/`;
      axios
        .get(path)
        .then(response => {
          this.repos = response.data.repos;
        })
        .catch(error => {
          console.log("Error! Could not reach the API. " + error);
        });
    }
  },
  created() {
    this.getRepos();
  }
};
</script>
