<template>
  <div class="dashboard contents">
    <div class="tile is-ancestor">
      <div class="tile is-parent is-horizontal is-4">
        <div class="tile is-child box">
          <p class="title is-size-5">
            {{ $t('message.dashboard.prj_usage') }}
          </p>
          <p>
            <ul>
              <li>
                <b>{{ $t('message.dashboard.account') }}:</b> {{ Account }}
              </li>
              <li>
                <b>
                  {{ $t('message.dashboard.containers') }}:
                </b> {{ Containers }}
              </li>
              <li>
                <b>{{ $t('message.dashboard.objects') }}:</b> {{ Objects }}
              </li>
              <li>
                <b>{{ $t('message.dashboard.usage') }}:</b> {{ Size }}
              </li>
            </ul>
          </p>
        </div>
      </div>
      <div class="tile is-parent is-horizontal is-8">
        <div class="tile is-child box">
          <p class="title is-size-5">
            {{ $t('message.dashboard.cur_billing') }}
          </p>
          <progress
            v-if="Bytes < (Bytes > 1099511627776 ? Bytes : 1099511627776)"
            class="progress is-success is-large"
            :value="Bytes"
            :max="Bytes > 1099511627776 ? Bytes : 1099511627776"
          >
            {{ parseInt(Bytes/1099511627776) }}
          </progress>
          <progress
            v-else
            class="progress is-danger is-large"
            :value="Bytes"
            :max="Bytes > 1099511627776 ? Bytes : 1099511627776"
          >
            {{ parseInt(Bytes/1099511627776) }}
          </progress>
          <p>
            <ul>
              <li>
                <b>{{ $t('message.dashboard.prj_str_usag') }}: </b>
                {{ Size }} / {{ ProjectSize }}
                <b-tooltip
                  v-if="!DisableTooltip"
                  size="is-large"
                  :label="$t('message.dashboard.default_notify')"
                  position="is-right"
                  multilined
                  always
                >
                  <b-icon
                    size="is-small"
                    icon="information"
                  />
                </b-tooltip>
                <b-tooltip
                  v-else
                  size="is-large"
                  :label="$t('message.dashboard.default_notify')"
                  position="is-right"
                  multilined
                >
                  <b-icon
                    size="is-small"
                    icon="information"
                  />
                </b-tooltip>
              </li>
              <li>
                <b>{{ $t('message.dashboard.equals') }}: </b>
                {{ Billed }} <b>BU / {{ $t('message.dashboard.hour') }} </b>
              </li>
            </ul>
          </p>
        </div>
      </div>
    </div>
    <div class="tile is-ancestor">
      <div class="tile is-parent is-horizontal is-12">
        <div class="tile is-child is-12 box">
          <p class="title is-size-5">
            {{ $t('message.dashboard.more_info') }}
          </p>
          <ul>
            <li 
              v-for="item in $t('message.dashboard.links')"
              :key="item.msg"
            >
              <a
                target="_blank"
                :href="item.href"
              >{{ item.msg }}</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div class="tile is-ancestor">
      <div class="tile is-parent is-horizontal is-12">
        <div class="tile is-child is-12 box">
          <p class="title is-size-5">
            {{ $t('message.dashboard.resources') }}
          </p>
          <div class="field has-addons">
            <p class="control">
              <b-button
                class="control"
                type="is-primary"
                outlined
                @click="$router.push({
                  name: 'TokensView',
                  params: {
                    project: $store.state.active.id
                  }
                })"
              >
                {{ $t('message.dashboard.tokens') }}
              </b-button>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getProjectMeta } from "@/common/api";

export default {
  name: "DashboardView",
  // The view for the application user page for showing the user
  // information in a bit more detail. Shows e.g. the storage
  // expenditure and the billing unit (BU) usage caused by that.
  data: function () {
    // Since we don't need the app for caching, we can use a more elegant
    // way of declaring the instance data
    return {
      Containers: 0,
      Objects: 0,
      Account: "",
      Size: 0,
      Billed: 0,
      Bytes: 0,
      DisableTooltip: false,
      ProjectSize: "10TiB",
    };
  },
  computed: {
    active () {
      return this.$store.state.active;
    },
  },
  beforeMount(){
    // Fetch relevant things upon initializing the class instance
    this.fetchMeta();
    this.disable();
  },
  methods: {
    fetchMeta: function () {
      // Get the project metadata from the API using the API convenience
      // function in api.js
      getProjectMeta(this.active.id).then((ret) => {
        this.Containers = ret["Containers"];
        this.Objects = ret["Objects"];
        this.Account = ret["Account"].replace("AUTH_", "");
        this.Size = ret["Size"];
        this.Billed = ret["Billed"];
        this.Bytes = ret["Bytes"];
        this.ProjectSize = ret["ProjectSize"];
      });
    },
    disable: function() {
      // Automatically display a tip / notification about the billing
      // units and related calculations. Also timeout said tip.
      if (document.cookie.match("DISABLE_BILLING_NOTE")) {
        this.DisableTooltip = true;
      }
      else {
        setTimeout(() => {
          this.DisableTooltip = true;
          document.cookie = "DISABLE_BILLING_NOTE=true";
        }, 4000);
      }
    },
  },
};
</script>
