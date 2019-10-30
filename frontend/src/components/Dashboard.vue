<template>
  <div class="main">
    <div class="spinner" v-if="loading">
      <button type="button" class="btn btn-primary">
        <i class="fa fa-spinner fa-spin"></i> Loading...
      </button>
    </div>
    <!-- MAIN CONTENT -->
    <div v-if="!loading" class="main-content">
      <div class="container-fluid">
        <div class="panel panel-headline">
          <div class="panel-heading">
            <h3 class="panel-title">Repos</h3>
          </div>
          <div class="panel-body">
            <div class="row">
              <repo-card v-for="(repo, index) in repos" :key="index" :repo="repo" />
            </div>
          </div>
          <div class="panel-heading">
            <h3 class="panel-title">Projects</h3>
          </div>
          <div class="panel-body">
            <div class="row">
              <project-card v-for="(project, index) in projects" :key="index" :project="project" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import repoCard from "./repoCard.vue";
import projectCard from "./projectCard.vue";

export default {
  name: "Dashboard",
  components: {
    "repo-card": repoCard,
    "project-card": projectCard
  },
  data() {
    return {
      loading: false,
      repos: null,
      projects: null
    };
  },
  methods: {
    getDetails() {
      this.getRepos();
    },
    getRepos() {
      this.loading = true; //the loading begin
      const path = `https://zeroci.grid.tf/api/`;
      axios
        .get(path)
        .then(response => {
          this.loading = false;
          this.repos = response.data.repos;
          this.projects = response.data.projects;
        })
        .catch(error => {
          this.loading = false;
          console.log("Error! Could not reach the API. " + error);
        });
    }
  },
  created() {
    this.getDetails();
  }
};
</script>

<style scoped>
.panel-headline {
  min-height: 83vh;
}
#wrapper .main,
.main .panel-headline {
  background-color: #dddde3;
}

.fa-1x {
  font-size: 0.9em;
}
</style>
