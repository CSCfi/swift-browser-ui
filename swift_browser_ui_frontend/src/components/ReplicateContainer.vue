<template>
  <div v-if="disabled">
    <b-button
      v-if="smallsize"
      type="is-primary"
      size="is-small"
      outlined
      disabled
      :inverted="inverted"
      icon-left="content-copy"
    >
      {{ $t('message.copy') }}
    </b-button>
    <b-button
      v-else
      type="is-primary"
      outlined
      :inverted="inverted"
      disabled
      icon-left="content-copy"
    >
      {{ $t('message.copy') }}
    </b-button>
  </div>
  <div v-else>
    <b-button
      v-if="smallsize"
      type="is-primary"
      size="is-small"
      outlined
      :inverted="inverted"
      icon-left="content-copy"
      @click="$router.push({
        name: 'ReplicateContainer',
        params: {
          container: getContainer(),
          project: getProject(),
          from: getFrom(),
        }
      })"
    >
      {{ $t('message.copy') }}
    </b-button>
    <b-button
      v-else
      type="is-primary"
      outlined
      :inverted="inverted"
      icon-left="content-copy"
      @click="$router.push({
        name: 'ReplicateContainer',
        params: {
          container: getContainer(),
          project: getProject(),
          from: getFrom(),
        }
      })"
    >
      {{ $t('message.copy') }}
    </b-button>
  </div>
</template>

<script>
export default {
  name: "ReplicateContainerButton",
  props: [
    "project",
    "container",
    "smallsize",
    "inverted",
    "disabled",
    "from",
  ],
  computed: {
    active () {
      return this.$store.state.active;
    },
  },
  methods: {
    getProject: function () {
      if(this.$route.params.user == undefined) {
        return this.$props.project ? this.$props.project :
          this.$route.params.project;
      }
      return this.active.id;
    },
    getFrom: function() {
      if (this.$props.from != undefined) {
        return this.$props.from;
      }
      return this.active.id;
    },
    getContainer: function () {
      return this.$props.container ? this.$props.container :
        this.$route.params.container;
    },
  },
};
</script>
