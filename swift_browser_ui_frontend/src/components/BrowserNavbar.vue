<template>
  <div
    id="navbar"
    class="navbar has-shadow"
  >
    <div class="container is-fluid">
      <div class="navbar-brand">
        <a
          class="navbar-item csclogo"
          :href="'/browse/'.concat(uname)"
        >
          <img
            src="@/assets/logo.svg"
            :alt="$t('message.cscOrg')"
          >
        </a>
      </div>
      <div class="navbar-menu">
        <div class="navbar-start">
          <div class="navbar-item">
            <b>{{ $t("message.program_name") }}</b>
          </div>
          <div 
            v-if="multipleProjects"
            class="navbar-item is-hoverable"
          >
            {{ $t("message.currentProj") }}: <a class="navbar-link">
              <span>{{ active.name }}</span>
            </a>

            <div class="navbar-dropdown">
              <a
                v-for="item in projects"
                :key="item.id"
                class="navbar-item"
                @click="changeActive(item)"
              ><span>{{ item.name }}</span></a>
            </div>
          </div>
          <div
            v-if="!multipleProjects"
            class="navbar-item"
          >
            {{ $t("message.currentProj") }}: &nbsp;<span>
              {{ active.name }}
            </span>
          </div>
        </div>
        <div class="navbar-end">
          <div
            v-if="$te('message.helplink')"
            class="navbar-item"
          >
            <div class="buttons">
              <a
                :href="$t('message.helplink')"
                target="_blank"
                class="button is-primary is-outlined"
              >{{ $t("message.help") }}</a>
            </div>
          </div>
          <div class="navbar-item">
            <div class="buttons">
              <router-link
                :to="{name: 'DashboardView', params: {user: uname}}"
                :class="!($route.name == 'DashboardView') ? 
                  'button is-primary is-outlined' : 
                  'button is-primary has-text-light'"
              >
                {{ $t("message.dashboard.dashboard") }}
              </router-link>
            </div>
          </div>
          <div class="navbar-item">
            <div class="buttons">
              <router-link
                :to="{name: 'ContainersView',
                      params: {user: uname, project: active.id}}"
                :class="!($route.name == 'ContainersView'
                  || $route.name == 'ObjectsView') ? 
                  'button is-primary is-outlined' : 
                  'button is-primary has-text-light'"
              >
                {{ $t("message.dashboard.browser") }}
              </router-link>
            </div>
          </div>
          <div
            v-if="$store.state.client"
            class="navbar-item"
          >
            <div class="buttons">
              <router-link
                :to="{name: 'SharedTo', params: {
                  user: uname,
                  project: active.id
                }}"
                :class="
                  !($route.name == 'SharedTo' ||
                    $route.name == 'SharedFrom' || 
                    $route.name == 'ShareRequests') ? 
                    'button is-primary is-outlined' : 
                    'button is-primary has-text-light'"
              >
                {{ $t("message.share.shared") }}
              </router-link>
            </div>
          </div>
          <div class="navbar-item">
            <b-field class="locale-changer">
              <b-select
                v-model="$i18n.locale"
                placeholder="Language"
                icon="earth"
                @input="setCookieLang ()"
              >
                <option 
                  v-for="lang in langs"
                  :key="lang.value"
                  :value="lang.value"
                >
                  {{ lang.ph }}
                </option>
              </b-select>
            </b-field>
          </div>
          <div class="navbar-item">
            <div class="buttons">
              <a
                class="button is-primary is-outlined"
                href="/login/kill"
              >{{ $t("message.logOut") }}</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "BrowserNavbar",
  props: [
    "langs",
    "multipleProjects",
    "projects",
  ],
  computed: {
    active () {
      return this.$store.state.active;
    },
    uname () {
      return this.$store.state.uname;
    },
  },
  methods: {
    setCookieLang: function() {
      const expiryDate = new Date();
      expiryDate.setMonth(expiryDate.getMonth() + 1);
      document.cookie = "OBJ_UI_LANG=" +
        this.$i18n.locale +
        "; path=/; expires="
        + expiryDate.toUTCString();
    },
    changeActive (item) {
      this.$store.commit("setActive", item);
      let newParams = Object.fromEntries(Object.entries(
        this.$route.params,
      ));
      if (newParams.project != undefined) {
        newParams.project = item.id;
      }
      this.$router.push({
        name: this.$route.name,
        params: newParams,
      });
    },
    getProjectChangeURL ( newProject ) {
      let rescopeURL = new URL(
        "/login/rescope",
        document.location.origin,
      );
      rescopeURL.searchParams.append( "project", newProject );
      return rescopeURL.toString();        
    },

  },
};
</script>
