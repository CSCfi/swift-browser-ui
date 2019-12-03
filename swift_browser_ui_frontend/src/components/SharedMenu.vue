<template>
  <b-menu>
    <b-menu-list>
      <b-menu-item
        label="Shared to the project"
        icon="folder-shared"
        tag="router-link"
        :to="{name :'SharedTo' ,params: {project: $route.params.project}}"
      />
      <b-menu-item
        label="Shared from the project"
        icon="share"
        tag="router-link"
        :to="{name: 'SharedFrom', params: {project: $route.params.project}}"
      />
      <b-menu-item
        label="Request access"
        icon="folder-plus"
        tag="router-link"
        :to="{name: 'ShareRequests', params: {project: $route.params.project}}"
      />
    </b-menu-list>
  </b-menu>
</template>

<script>
export default {
  name: "SharedMenu",
};
</script>
