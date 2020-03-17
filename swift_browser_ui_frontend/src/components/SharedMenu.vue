<template>
  <b-menu>
    <b-menu-list>
      <b-menu-item
        :label="$t('message.share.to_me')"
        icon="folder-account"
        tag="router-link"
        :to="{name :'SharedTo' ,params: {project: $route.params.project}}"
        :active="$route.name == 'SharedTo' ? true : false"
      />
      <b-menu-item
        :label="$t('message.share.from_me')"
        icon="share"
        tag="router-link"
        :to="{name: 'SharedFrom', params: {project: $route.params.project}}"
        :active="$route.name == 'SharedFrom' ? true : false"
      />
      <b-menu-item
        :label="$t('message.share.request_sharing')"
        icon="folder-plus"
        tag="router-link"
        :to="{name: 'ShareRequests', params: {project: $route.params.project}}"
        :active="$route.name == 'ShareRequests' ? true : false"
      />
    </b-menu-list>
  </b-menu>
</template>

<style>
.menu-list {
  border: solid 1px #dbdbdb;
  border-radius: 6px;
}
.menu-list li a {
  padding: 0.8em;
}
.menu-list li {
  border-bottom: solid 1px #dbdbdb;
}
.menu-list li:last-child {
  border-bottom: none;
}
</style>

<script>
export default {
  name: "SharedMenu",
};
</script>
