<template>
  <div class="contents">
    <b-field
      horizontal
      :label="$t('message.request.container')"
      :message="$t('message.request.container_message')"
    >
      <b-input 
        v-model="container"
        name="container"
        expanded
        aria-required="true"
      />
    </b-field>

    <b-field
      horizontal
    >
      <p class="control">
        <button
          class="button is-primary"
          @click="createContainer ()"
        >
          {{ $t('message.copy') }}
        </button>
      </p>
    </b-field>
  </div>
</template>

<script>
import {swiftCreateContainer} from "@/common/api";

export default {
  name: "CreateContainer",
  data () {
    return {
      container: "",
    };
  },
  methods: {
    createContainer: function () {
      swiftCreateContainer(this.container).then(() => {
        this.$router.go();
      });
    },
  },
};
</script>
