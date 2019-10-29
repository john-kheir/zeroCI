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
        <div class="row">
          <div class="col-md-12">
            <!-- Logs -->
            <div class="panel" v-for="(log, index) in logs" :key="index">
              <div class="panel-heading">
                <h3 class="panel-title">
                  <span class="d-block">
                    <b>Name:</b>
                    {{ log.name }}
                  </span>
                  <span>
                    <b>Status:</b>
                  </span>
                  <span
                    class="label"
                    :class="{
                      'label-success': log.status== 'success',
                      'label-warning': log.status== 'error',
                      'label-danger': (log.status== 'failure')
                      }"
                  >{{ log.status }}</span>
                </h3>
              </div>
              <div class="panel-body">
                <pre><code>{{ log.content }}</code></pre>
              </div>
            </div>
            <!-- testsuites -->
            <div class="panel" v-for="(testsuite, i) in testsuites" :key="`A-${i}`">
              <!-- head: name, status -->
              <div class="panel-heading">
                <h3 class="panel-title">
                  <span class="d-block">
                    <b>Name:</b>
                    {{testsuite.name}}
                  </span>
                  <span>
                    <b>Status:</b>
                  </span>
                  <span
                    class="label"
                    :class="{
                      'label-success': testsuite.status== 'success',
                      'label-warning': testsuite.status== 'pending',
                      'label-danger': (testsuite.status== 'failure') || (testsuite.status== 'error')
                      }"
                  >{{ testsuite.status }}</span>
                </h3>
              </div>
              <!-- body: Tabs and result -->
              <div class="panel-body">
                <!-- tabs -->
                <ul class="nav nav-tabs" role="tablist">
                  <li role="presentation" class="active">
                    <a :href="'#all-' + i" aria-controls="all" role="tab" data-toggle="tab">
                      All&nbsp;
                      <span class="badge">{{ summary[i].tests }}</span>
                    </a>
                  </li>
                  <li role="presentation">
                    <a :href="'#failed-' + i" aria-controls="failed" role="tab" data-toggle="tab">
                      Failed&nbsp;
                      <span class="badge">{{ summary[i].failures }}</span>
                    </a>
                  </li>
                  <li role="presentation">
                    <a :href="'#errored-' + i" aria-controls="errored" role="tab" data-toggle="tab">
                      Errored&nbsp;
                      <span class="badge">{{ summary[i].errors }}</span>
                    </a>
                  </li>
                  <li role="presentation">
                    <a :href="'#skipped-' + i" aria-controls="skipped" role="tab" data-toggle="tab">
                      Skipped&nbsp;
                      <span class="badge">{{ summary[i].skip }}</span>
                    </a>
                  </li>
                </ul>
                <!-- tabs content -->
                <div class="tab-content">
                  <div role="tabpanel" class="tab-pane fade in active" :id="'all-' + i">
                    <div
                      class="panel-group"
                      id="accordion"
                      role="tablist"
                      aria-multiselectable="true"
                    >
                      <div
                        class="panel"
                        v-for="(testcase, key) in testsuite.content.testcases"
                        :key="key"
                      >
                        <div class="panel-heading" role="tab">
                          <h4 class="panel-title">
                            <a
                              role="button"
                              data-toggle="collapse"
                              data-parent="#accordion"
                              :href="'#all-'+key+1"
                              @click="selectItem(key)"
                              aria-expanded="true"
                              :aria-controls="'collapse-'+key+1"
                            >
                              <i
                                class="fa"
                                :class="{
                                  'fa-check-circle success': testcase.status== 'passed',
                                  'fa-times-circle danger': testcase.status== 'failed',
                                  'fa-minus-circle danger': testcase.status== 'errored',
                                  'fa-ban': testcase.status== 'skipped'}"
                              ></i>
                              {{ testcase.classname }} {{ testcase.name }}
                            </a>
                          </h4>
                        </div>
                        <div
                          :id="'all-'+key+1"
                          class="panel-collapse collapse"
                          :class="{ in: key === activeItem} "
                          role="tabpanel"
                          :aria-labelledby="'all-'+key+1"
                        >
                          <div class="panel-body">
                            <pre><code>{{ testcase.status }} &nbsp; (Executed in {{ testcase.time }} seconds)</code>
                            <code v-if="testcase.details">{{ testcase.details.content }} <br />{{ testcase.details.message }}</code></pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div role="tabpanel" class="tab-pane fade" :id="'failed-' + i">
                    <div
                      class="panel-group"
                      id="accordion"
                      role="tablist"
                      aria-multiselectable="true"
                    >
                      <div
                        class="panel"
                        v-for="(testcase, key) in testsuite.content.testcases"
                        :key="key"
                        v-show="testcase.status == 'failed'"
                      >
                        <div class="panel-heading" role="tab">
                          <h4 class="panel-title">
                            <a
                              role="button"
                              data-toggle="collapse"
                              data-parent="#accordion"
                              :href="'#failed-'+key+1"
                              @click="selectItem(key)"
                              aria-expanded="true"
                              :aria-controls="'collapse-'+key+1"
                            >
                              <i
                                class="fa"
                                :class="{
                                  'fa-check-circle success': testcase.status== 'passed',
                                  'fa-minus-circle danger': testcase.status== 'errored',
                                  'fa-times-circle danger': testcase.status== 'failed',
                                  'fa-ban': testcase.status== 'skipped'}"
                              ></i>
                              {{ testcase.classname }} {{ testcase.name }}
                            </a>
                          </h4>
                        </div>
                        <div
                          :id="'failed-'+key+1"
                          class="panel-collapse collapse"
                          :class="{ in: key === activeItem}"
                          role="tabpanel"
                          :aria-labelledby="'failed-'+key+1"
                        >
                          <div class="panel-body">
                            <pre><code>{{ testcase.status }} &nbsp; (Executed in {{ testcase.time }} seconds)</code> <hr />
                            <code v-if="testcase.details">{{ testcase.details.content }}<br />{{ testcase.details.message }}</code></pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div role="tabpanel" class="tab-pane fade" :id="'errored-' + i">
                    <div
                      class="panel-group"
                      id="accordion"
                      role="tablist"
                      aria-multiselectable="true"
                    >
                      <div
                        v-for="(testcase, key) in testsuite.content.testcases"
                        :key="key"
                        class="panel"
                        v-show="testcase.status == 'errored'"
                      >
                        <div class="panel-heading" role="tab">
                          <h4 class="panel-title">
                            <a
                              role="button"
                              data-toggle="collapse"
                              data-parent="#accordion"
                              :href="'#errored-'+key+1"
                              @click="selectItem(key)"
                              aria-expanded="true"
                              :aria-controls="'collapse-'+key+1"
                            >
                              <i class="fa fa-minus-circle danger"></i>
                              {{ testcase.classname }} {{ testcase.name }}
                            </a>
                          </h4>
                        </div>
                        <div
                          :id="'errored-'+key+1"
                          class="panel-collapse collapse"
                          :class="{ in: key === activeItem}"
                          role="tabpanel"
                          :aria-labelledby="'errored-'+key+1"
                        >
                          <div class="panel-body">
                            <pre>
                            <code>{{ testcase.status }} &nbsp; (Executed in {{ testcase.time }} seconds)</code> <hr />
                            <code v-if="testcase.details">{{ testcase.details.content }}<br />{{ testcase.details.message }}</code>
                            </pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div role="tabpanel" class="tab-pane fade" :id="'skipped-' + i">
                    <div
                      class="panel-group"
                      id="accordion"
                      role="tablist"
                      aria-multiselectable="true"
                    >
                      <div
                        v-for="(testcase, key) in testsuite.content.testcases"
                        :key="key"
                        class="panel"
                        v-show="testcase.status == 'skipped'"
                      >
                        <div class="panel-heading" role="tab">
                          <h4 class="panel-title">
                            <a
                              role="button"
                              data-toggle="collapse"
                              data-parent="#accordion"
                              :href="'#skipped-'+key+1"
                              @click="selectItem(key)"
                              aria-expanded="true"
                              :aria-controls="'collapse-'+key+1"
                            >
                              <i class="fa fa-ban"></i>
                              {{ testcase.classname }} {{ testcase.name }}
                            </a>
                          </h4>
                        </div>
                        <div
                          :id="'skipped-'+key+1"
                          class="panel-collapse collapse"
                          :class="{ in: key === activeItem} "
                          role="tabpanel"
                          :aria-labelledby="'skipped-'+key+1"
                        >
                          <div class="panel-body">
                            <pre>
                            <code>{{ testcase.status }} &nbsp; (Executed in {{ testcase.time }} seconds)</code> <hr / >
                            <code v-if="testcase.details">{{ testcase.details.content }} <br />{{ testcase.details.message }}</code>
                            </pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
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
  name: "deta",
  props: ["name", "id"],
  data() {
    return {
      data: null,
      loading: false,
      logs: [],
      testsuites: [],
      summary: [],
      testcases: [],
      activeItem: null
    };
  },
  methods: {
    getDetails() {
      this.data = this.getData();
    },
    getData() {
      this.loading = true;
      const path = `https://zeroci.grid.tf/api/projects/${this.name}?id=${this.id}`;
      axios
        .get(path)
        .then(response => {
          this.loading = false;
          this.data = response.data;
          this.data.map((job, index) => {
            if (job.type == "log") {
              this.logs.push(job);
            } else if (job.type == "testsuite") {
              this.testsuites.push(job);
              this.summary.push(job.content.summary);
              this.testcases.push(job.content.testcases);
            }
          });
        })
        .catch(error => {
          this.loading = false;
          console.log("Error! Could not reach the API. " + error);
        });
    },
    selectItem(i) {
      this.activeItem = i;
    }
  },
  created() {
    this.getDetails();
  }
};
</script>

