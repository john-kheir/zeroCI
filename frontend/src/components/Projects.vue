<template>
  <ul class="nav">
    <li style="color: #fff;padding: 15px;">
      <i class="lnr lnr-book"></i>
      <span>Projects</span>
    </li>
    <li v-for="(project, index) in projects" :key="index">
      <router-link :to="'/projects/' + project">{{ project }}</router-link>
    </li>
  </ul>
</template>

<script>
import axios from "axios";

export default {
  name: "Items",
  data() {
    return {
      projects: null
    };
  },
  methods: {
    getOrgs() {
      this.getData();
    },
    getData() {
      const path = `https://zeroci.grid.tf/api/`;
      axios
        .get(path)
        .then(response => {
          this.projects = response.data.projects;
        })
        .catch(error => {
          console.log("Error! Could not reach the API. " + error);
        });
    }
  },
  created() {
    this.getOrgs();
  }
};
</script>
