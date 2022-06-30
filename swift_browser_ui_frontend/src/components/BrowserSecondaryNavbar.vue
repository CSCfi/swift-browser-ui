<template>
  <div id="secondary-navbar-wrapper">
    <div
      id="secondary-navbar"
      class="navbar"
    >
      <div class="container is-fluid">
        <div class="navbar-menu">
          <div class="navbar-start">
            <div 
              v-if="multipleProjects"
              class="navbar-item"
            >
              <c-select
                v-bind="active"
                c-control
                :items.prop="mappedProjects"
                :label="$t('message.selectProj')"
                placeholder="Select project"
                return-value
                hide-details
                class="select-project"
                data-testid="project-selector"
                @changeValue="changeActive($event)"
              />
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
              <c-button @click="$router.push({ name: 'AddContainer'})">
                {{ $t('message.createFolder') }}
              </c-button>
            </div>
            <div class="navbar-item">
              <c-button
                outlined
                @click="$router.push({ name: 'UploadView', params: {
                  project: $route.params.project,
                  container: 'upload-'.concat(Date.now().toString()),
                }})"
              >
                {{ $t('message.uploadSecondaryNav') }}
              </c-button>
            </div>
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
      const activeObject = this.$store.state.active;
      return {...activeObject, value: activeObject.id};
    },
    uname () {
      return this.$store.state.uname;
    },
    // C-select component handles options by name and value props
    // Append value-prop to projects
    mappedProjects () {
      return this.projects.map(project => ({...project, value: project.id}));
    },
  },
  methods: {
    changeActive (event) {
      const item = event.target.value;
      if (item.id !== this.active.id){
        const navigationParams = {
          name: "ContainersView", 
          params: {user: this.uname, project: item.id},
        };

        // Pushing to router before ´go´ method
        // enables navigation with updated item id
        this.$router.push(navigationParams);
        this.$router.go(navigationParams);
      }
    },
  },
};
</script>

<style scoped lang="scss">
@import "@/css/prod.scss";

#secondary-navbar {
 border-bottom: 6px solid $csc-primary-light;
 min-height: 5rem;
}

.navbar-item:first-of-type {
  padding-left: 0;
}

.select-project {
  padding: 0.5rem 0;
}
</style>
