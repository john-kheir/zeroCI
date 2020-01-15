<template>
  <div class="main">
    <div class="spinner" v-if="loading">
      <button type="button" class="btn btn-primary">
        <i class="fa fa-spinner fa-spin"></i> Loading...
      </button>
    </div>
    <!-- MAIN CONTENT -->
    <div class="main-content">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-6">
            <h3 class="page-title">{{ name }}</h3>
            <div class="panel panel-default">
              <div class="panel-body">
                <!-- PANEL HEADLINE -->
                <h4>Branches:</h4>
                <ul >
                  <li v-for="(branch, key) in branches" :key="key + 'a'">
                    <router-link :to="'/repos/' + repoName + '/' + branch">{{branch}}</router-link>
                  </li>
                </ul>
                <h4 style="color:red">Deleted:</h4>
                <ul >
                  <li v-for="(del, key) in deleted" :key="key">
                    <router-link :to="'/repos/' + repoName + '/' + del">{{del}}</router-link>
                  </li>
                </ul>
                <!-- END PANEL HEADLINE -->
                <!-- END MAIN CONTENT -->
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name: "Branches",
  props: ["name"],
  data() {
    return {
      branches: null,
      deleted: null,
      loading: false
    };
  },
  computed: {
    repoName: function() {
      return this.name.replace("/", "%2F");
    }
  },
  methods: {
    clear() {
      this.branches = null;
      this.deleted = null;
    },
    getBranches(name) {
      this.loading = true; //the loading begin
      const path = `https://zeroci.grid.tf/api/repos/${this.repoName}`;
      axios
        .get(path)
        .then(response => {
          this.loading = false;
          this.branches = response.data.exist;
          this.deleted = response.data.deleted;
        })
        .catch(error => {
          this.loading = false;
          console.log("Error! Could not reach the API. " + error);
        });
    }
  },
  created() {
    this.getBranches(name);
  },
  watch: {
    "$route.params": {
      handler(newValue) {
        this.clear();
        const { name } = newValue;
        this.getBranches(name);
      },
      immediate: true
    }
  }
};
</script>
