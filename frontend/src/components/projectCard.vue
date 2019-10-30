<template>
  <div class="col-md-3">
    <router-link :to="'/projects/' + projectName + '/' + id">
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
            <h5>{{ project }}</h5>
            <h2>{{ status }}</h2>
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
  name: "projectCard",
  props: ["project"],
  data() {
    return {
      pro: null,
      timestamp: null,
      status: null,
      id: null,
      filteredItems: []
    };
  },
  methods: {
    getProjectData() {
      const path = `https://zeroci.grid.tf/api/projects/${this.project}`;
      axios
        .get(path)
        .then(response => {
          this.loading = false;
          this.pro = response.data;
          this.filteredItems = this.pro.filter(
            item => item.status !== "pending"
          );
          this.timestamp = this.filteredItems[0].timestamp;
          this.status = this.filteredItems[0].status;
          this.id = this.filteredItems[0].id;
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
    projectName: function() {
      return this.project.replace(" ", "%20");
    }
  },
  created() {
    this.getProjectData();
  }
};
</script>
