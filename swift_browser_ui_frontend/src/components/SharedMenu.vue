<template>
  <b-menu>
    <b-menu-list>
      <b-menu-item
        icon="folder-account"
        tag="router-link"
        :label="$t('message.share.to_me')"
        :to="{name :'SharedTo' ,params: {
          user: user,
          project: project,
        }}"
        :active="name == 'SharedTo' ? true : false"
      />
      <b-menu-item
        icon="share"
        tag="router-link"
        :label="$t('message.share.from_me')"
        :to="{name: 'SharedFrom', params: {
          user: user,
          project: project,
        }}"
        :active="name == 'SharedFrom' ? true : false"
      />
      <b-menu-item
        icon="folder-plus"
        tag="router-link"
        :label="$t('message.share.request_sharing')"
        :to="{name: 'ShareRequests', params: {
          user: user,
          project: project,
        }}"
        :active="name == 'ShareRequests' ? true : false"
      />
    </b-menu-list>
  </b-menu>
</template>

<script>
export default {
  name: "SharedMenu",
  computed: {
    project () {
      return this.$route.params.project;
    },
    user () {
      return this.$route.params.user;
    },
    name () {
      return this.$route.name;
    },
  },
};
</script>


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
