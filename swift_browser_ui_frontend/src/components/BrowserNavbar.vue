<template>
  <div
    id="navbar"
    class="navbar has-shadow"
  >
    <div class="container is-fluid">
      <div class="navbar-brand">
        <a
          class="navbar-item csclogo"
          href="#"
        >
          <img
            src="@/assets/csc_logo.svg"
            :alt="$t('message.cscOrg')"
          >
        </a>
      </div>
      <div class="navbar-menu">
        <div class="navbar-start">
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
                :href="getProjectChangeURL ( item.id )"
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
          <div class="navbar-item">
            <div class="buttons">
              <router-link
                v-if="$route.params.project == undefined"
                :to="'/browse/' + $route.params.user + '/' + active.name"
                class="button is-primary has-text-light"
              >
                {{ $t("message.dashboard.browser") }}
              </router-link>
              <router-link
                v-else 
                :to="'/browse/' + $route.params.user"
                class="button is-primary has-text-light"
              >
                {{ $t("message.dashboard.dashboard") }}
              </router-link>
            </div>
          </div>
          <div
            v-if="$store.state.client"
            class="navbar-item"
          >
            <div class="buttons">
              <router-link
                v-if="$route.params.project"
                :to="'/browse/sharing/to/'.concat(active.id)"
                class="button is-primary has-text-light"
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
                class="button is-primary has-text-light"
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
    "active",
  ],
  methods: {
    setCookieLang: function() {
      const expiryDate = new Date();
      expiryDate.setMonth(expiryDate.getMonth() + 1);
      document.cookie = "OBJ_UI_LANG=" +
        this.$i18n.locale +
        "; path=/; expires="
        + expiryDate.toUTCString();
    },
    getProjectChangeURL ( newProject ) {
      let rescopeURL = new URL(
        "/login/rescope",
        document.location.origin
      );
      rescopeURL.searchParams.append( "project", newProject );
      return rescopeURL.toString();        
    },

  },
};
</script>
