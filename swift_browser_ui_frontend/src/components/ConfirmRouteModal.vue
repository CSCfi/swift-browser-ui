<template>
  <c-card
    class="confirm-route-modal"
  >
    <c-alert type="warning">
      <div slot="title">
        {{ $t("message.route.title") }}
      </div>
      {{ $t("message.route.text") }}
      <c-card-actions justify="end">
        <c-button
          outlined
          @click="closeConfirmRouteModal(false)"
          @keyup.enter="closeConfirmRouteModal(true)"
        >
          {{ $t("message.route.cancel") }}
        </c-button>
        <c-button
          @click="confirm(false)"
          @keyup.enter="confirm(true)"
        >
          {{ $t("message.route.confirm") }}
        </c-button>
      </c-card-actions>
    </c-alert>
  </c-card>
</template>

<script>

export default {
  name: "ConfirmRouteModal",
  computed: {
    active() {
      return this.$store.state.active;
    },
    params() {
      return this.$store.state.routeTo;
    },
  },
  methods: {
    confirm() {
      if (this.params) {
        this.$router.push(this.params).then(() => {
          this.$router.go(0);
        });
      }
      this.closeConfirmRouteModal();
    },
    closeConfirmRouteModal() {
      this.$store.commit("toggleConfirmRouteModal", false);
      //routeTo project param is key for c-select:
      //updating it causes to rerender with correct value
      this.$store.commit("setRouteTo", {});
    },
  },
};
</script>

<style scoped lang="scss">

@import "@/css/prod.scss";

.confirm-route-modal {
  padding: 0px;
}

</style>
