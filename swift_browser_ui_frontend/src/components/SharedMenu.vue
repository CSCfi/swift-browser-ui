<template>
  <b-menu>
    <b-menu-list>
      <b-menu-item
        :label="$t('message.share.to_me')"
        icon="folder-shared"
        tag="router-link"
        :to="{name :'SharedTo' ,params: {project: $route.params.project}}"
      />
      <b-menu-item
        :label="$t('message.share.from_me')"
        icon="share"
        tag="router-link"
        :to="{name: 'SharedFrom', params: {project: $route.params.project}}"
      />
      <b-menu-item
        :label="$t('message.share.request_sharing')"
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
