<template>
  <div 
    id="addview"
    class="contents"
  >
    <h1 class="title is-3 addcontainerhead">
      Add a new container
    </h1>
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
        <b-button
          type="is-primary"
          class="addcontainerbutton"
          @click="createContainer ()"
        >
          {{ $t('message.create') }}
        </b-button>
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

<style scoped>
  #addview {
    width: auto;
    margin-left: 5%;
    margin-right: 5%;
  }
  .addcontainerhead {
    margin: 1% 1% 1% 0;
  }
  .addcontainerbutton {
    margin: 1%;
  }
</style>
