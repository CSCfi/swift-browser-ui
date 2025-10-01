<template>
  <div>
  <c-row
    v-for="(item, i) in validationCriteria"
    :key="i"
    align="center"
    gap="10"
    nowrap
  >
    <c-icon
      :color="`var(--csc-${item.type})`"
      :path="
        item.type === 'success'
          ? mdiCheckCircle
          : item.type === 'error'
          ? mdiCloseCircle
          : mdiInformation
      "
    />
    <span
      :data-testid="`name-validation-${item.type}`"
    >
      {{ item.message }}
    </span>
  </c-row>
  </div>
</template>

<script>
import { mdiInformation, mdiCheckCircle, mdiCloseCircle } from "@mdi/js";

export default {
  name: "BucketNameValidation",
  props: {
    result: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      mdiInformation,
      mdiCheckCircle,
      mdiCloseCircle,
    };
  },
  computed: {
    validationCriteria() {
      return [
        {
          message: this.$t("message.nameValidation.lowerCaseOrNum"),
          type: this.getType("lowerCaseOrNum"),
        },
        {
          message: this.$t("message.nameValidation.inputLength"),
          type: this.getType("inputLength"),
        },
        {
          message: this.$t("message.nameValidation.alphaNumHyphen1"),
          type: this.getType("alphaNumHyphen"),
        },
        {
          message: this.$t("message.nameValidation.alphaNumHyphen2"),
          type: this.getType("alphaNumHyphen"),
        },
        {
          message: this.$t("message.nameValidation.ownable"),
          type: this.getType("ownable"),
        },
      ];
    },
  },
  methods: {
    getType(check) {
      return this.result?.[check]
        ? "success"
        : this.result?.[check] === false
          ? "error"
          : "info";
    },
  },
};
</script>

<style scoped>
span {
  font-size: 0.875rem;
  margin: 5px 0;
}
</style>
