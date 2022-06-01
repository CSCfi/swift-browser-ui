<template>
  <div
    id="secondary-navbar"
    class="navbar"
  >
    <div class="container is-fluid">
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
              <router-link
                v-for="item in projects"
                :key="item.id"
                :to="{
                  name: 'ContainersView', 
                  params: {user: uname, project: item.id}
                }"
                class="navbar-item"
                @click.native.stop="changeActive(item)"
              >
                {{ item.name }}
              </router-link>
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
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "BrowserSecondaryNavbar",
  props: [
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
    changeActive (item) {
      if (item.id !== this.active.id){
        this.$router.go({
          name: "ContainersView", 
          params: {user: this.uname, project: item.id},
        });
      }
    },
  },
};
</script>

<style>
#secondary-navbar {
 border-bottom: 6px solid #C2DBDF
}
</style>
