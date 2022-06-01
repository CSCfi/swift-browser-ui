<template>
  <div
    id="main-navbar"
    class="navbar"
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
                :to="{
                  name: 'DashboardView', 
                  params: {user: uname, project: active.id}
                }"
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
                data-testid="logout"
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
  name: "BrowserMainNavbar",
  props: [
    "langs",
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
  },
};
</script>

<style lang="scss">
#main-navbar {
  box-shadow: 2px 4px 8px 0px #00000040;
  z-index: 31;
}
</style>
