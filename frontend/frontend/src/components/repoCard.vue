<template>
  <div class="col-md-3" v-if="visibility">
    <router-link :to="'/repos/' + repoName + '/' + 'development' + '/' + id">
      <div class="wrapper">
        <div class="row">
          <div
            class="col-xs-1 state"
            :class="{
            'label-success': status == 'success',
            'label-warning': status == 'error',
            'label-danger': status == 'failure'}"
          ></div>
          <div class="col-xs-10">
            <h5>{{ repo }}</h5>
            <h2>{{ status }}</h2>
            <img :src="committerAvatar" :alt="committer" />
            <span>{{ committer }}</span>
            <small>
              <i class="far fa-clock fa-1x"></i>
              {{ time2TimeAgo(timestamp) }}
            </small>
          </div>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "repoCard",
  props: ["repo"],
  data() {
    return {
      branches: null,
      committer: null,
      timestamp: null,
      status: null,
      id: null,
      filteredItems: [],
      avatar: null,
      visibility: true
    };
  },
  methods: {
    getBranchData() {
      const path = `https://zeroci.grid.tf/api/repos/${this.repo}?branch=development`;
      axios
        .get(path)
        .then(response => {
          this.loading = false;
          this.branches = response.data;
          if (this.branches.length > 0) {
            this.filteredItems = this.branches.filter(
              item => item.status !== "pending"
            );
            this.committer = this.filteredItems[0].committer;
            this.timestamp = this.filteredItems[0].timestamp;
            this.status = this.filteredItems[0].status;
            this.id = this.filteredItems[0].id;
          } else {
            this.visibility = false;
          }
        })
        .catch(error => {
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
  computed: {
    repoName: function() {
      return this.repo.replace("/", "%2F");
    },
    committerAvatar: function() {
      this.avatar = `https://github.com/${this.committer}.png?size=20`;
      return this.avatar;
    }
  },
  created() {
    this.getBranchData();
  }
};
</script>

<style scoped>
img {
  border-radius: 50%;
  margin-right: 5px;
  max-width: 20px;
  max-height: 20px;
}

small {
  margin-top: 2px;
}
</style>
