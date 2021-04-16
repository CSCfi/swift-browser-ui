<template>
  <div>
    <a
      :id="id"
      class="button is-outlined is-primary"
    >
      <b-icon
        icon="upload"
        size="is-small"
      />{{ $t('message.upload') }}
    </a>
  </div>
</template>

<script>
export default {
  name: "UploadButton",
  props: ["id"],
  computed: {
    res () {
      return this.$store.state.resumableClient;
    },
  },
  mounted () {
    this.registerToResumable();
  },
  activated () {
    this.registerToResumable();
  },
  methods: {
    registerToResumable: function () {
      this.res.assignBrowse(document.getElementById(this.$props.id));
    },
  },
};
</script>
