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
          <div class="col-md-12">
            <h3 class="page-title">{{ name }}</h3>
            <!-- PANEL -->
            <div class="panel">
              <div class="panel-body">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>#ID</th>
                      <th>Timestamp</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(project, index) in projects" :key="index">
                      <td>
                        <router-link
                          :to="'/projects/' + name + '/' + project.id"
                        >{{ projects.length - index }}</router-link>
                      </td>
                      <td>{{ time2TimeAgo(project.timestamp) }}</td>
                      <td>
                        <span
                          class="label"
                          :class="{
                            'label-success': project.status== 'success',
                            'label-danger': project.status== ('failure')  || project.status== ('error'),
                            'label-warning': project.status== 'pending',
                            }"
                        >{{ project.status }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <!-- END TABLE STRIPED -->
              </div>
            </div>
            <!-- END PANEL -->
          </div>
        </div>
      </div>
    </div>
    <!-- END MAIN CONTENT -->
  </div>
</template>
<script>
import axios from "axios";
export default {
  name: "MainSec",
  props: ["name"],
  data() {
    return {
      projects: null,
      loading: false
    };
  },
  methods: {
    clear() {
      this.projects = null;
    },
    getPro() {
      this.loading = true;
      const path = `https://zeroci.grid.tf/api/projects/${this.name}`;
      axios
        .get(path)
        .then(response => {
          this.loading = false;
          this.projects = response.data;
        })
        .catch(error => {
          this.loading = false;
          console.log("Error! Could not reach the API. " + error);
        });
    },
    time2TimeAgo(ts) {
      var d = new Date();
      var nowTs = Math.floor(d.getTime() / 1000);
      var seconds = nowTs - ts;

      // more that two days
      if (seconds > 2 * 24 * 3600) {
        return "a few days ago";
      }
      // a day
      if (seconds > 24 * 3600) {
        return "yesterday";
      }

      if (seconds > 3600) {
        return "a few hours ago";
      }
      if (seconds > 1800) {
        return "Half an hour ago";
      }
      if (seconds > 60) {
        return Math.floor(seconds / 60) + " minutes ago";
      }
    }
  },
  created() {
    this.getPro();
  },
  watch: {
    "$route.params": {
      handler(newValue) {
        this.clear();
        const { name } = newValue;
        this.getPro(name);
      },
      immediate: true
    }
  }
};
</script>
