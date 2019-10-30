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
          <!-- TABLE STRIPED -->
          <div class="panel">
            <div class="panel-heading">
              <h3 class="page-title">
                <b>Branch:</b>
                {{ branch }}
              </h3>
            </div>
            <div class="panel-body">
              <table class="table table-striped">
                <thead>
                  <tr>
                    <th>#ID</th>
                    <th>Author</th>
                    <th>Commit</th>
                    <th>Timestamp</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(value, key) in branchDetails" :key="key">
                    <td>
                      <router-link
                        :to="'/repos/' + repoName + '/' + branch + '/' + value.id"
                      >{{ branchDetails.length - key }}</router-link>
                    </td>
                    <td>
                      <img :src="committerAvatar(value.committer)" :alt="value.committer" />
                      <a :href="committer(value.committer)" target="_blank">{{ value.committer }}</a>
                    </td>
                    <td>
                      <a
                        :href="commit(value.commit)"
                        target="_blank"
                      >{{ value.commit.substring(0,8) }}</a>
                    </td>
                    <td>{{ time2TimeAgo(value.timestamp) }}</td>
                    <td>
                      <span
                        class="label"
                        :class="{ 'label-success': value.status== 'success', 'label-warning': value.status== 'pending', 'label-danger': (value.status== 'failure' || value.status== 'error' )}"
                      >{{ value.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <!-- END TABLE STRIPED -->
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import axios from "axios";

export default {
  name: "RepoDetails",
  props: ["name", "branch"],
  data() {
    return {
      branchDetails: null,
      fullpath: this.$route.fullPath,
      loading: false
    };
  },
  computed: {
    repoName: function() {
      return this.name.replace("/", "%2F");
    }
  },
  methods: {
    getDetails() {
      this.branchDetails = this.getData();
    },
    getData() {
      this.loading = true;
      const path = `https://zeroci.grid.tf/api/repos/${this.repoName}?branch=${this.branch}`;
      axios
        .get(path)
        .then(response => {
          this.loading = false;
          this.branchDetails = response.data;
        })
        .catch(error => {
          this.loading = false;
          console.log("Error! Could not reach the API. " + error);
        });
    },
    committer(value) {
      return `https://github.com/${value}`;
    },
    commit(value) {
      return `https://github.com/${this.name}/commit/${value}`;
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
    },
    committerAvatar: function(committer) {
      return `https://github.com/${committer}.png?size=20`;
    }
  },
  created() {
    this.getDetails();
  }
};
</script>

<style scoped>
img {
  border-radius: 50%;
  max-width: 20px;
  max-height: 20px;
}
</style>

