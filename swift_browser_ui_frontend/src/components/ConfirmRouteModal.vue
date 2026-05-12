<template>
  <c-card
    ref="confirmRouteModal"
    class="no-padding-card"
    @keydown="handleKeyDown"
  >
    <c-alert type="warning">
      <div slot="title">
        {{ $t("message.route.title") }}
      </div>
      {{ $t("message.route.text") }}
      <c-card-actions justify="end">
        <c-button
          outlined
          @click="closeConfirmRouteModal"
          @keyup.enter="closeConfirmRouteModal"
        >
          {{ $t("message.route.cancel") }}
        </c-button>
        <c-button
          @click="confirm"
          @keyup.enter="confirm"
        >
          {{ $t("message.route.confirm") }}
        </c-button>
      </c-card-actions>
    </c-alert>
  </c-card>
</template>

<script>
import { captureKeyboardNavInsideModal } from "@/common/keyboardNavigation";


export default {
  name: "ConfirmRouteModal",
  computed: {
    active() {
      return this.$store.active;
    },
    params() {
      return this.$store.routeTo;
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
      this.$store.toggleConfirmRouteModal(false);
      //routeTo project param is key for c-select:
      //updating it causes to rerender with correct value
      this.$store.setRouteTo({});
    },
    handleKeyDown(e) {
      if (e.key === "Escape") {
        this.$store.toggleConfirmRouteModal(false);
      } else {
        captureKeyboardNavInsideModal(e, this.$refs.confirmRouteModal);
      }
    },
  },
};
</script>
