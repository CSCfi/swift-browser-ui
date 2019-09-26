<template>
  <form action="">
    <div
      class="modal-card"
      style="width: auto;"
    >
      <header class="modal-card-head">
        <p class="modal-card-title">
          {{ $t('message.share.share_cont') }}
        </p>
      </header>
      <section class="modal-card-body">
        <b-field grouped>
          <b-switch
            v-model="read"
          >
            {{ $t('message.share.read_perm') }}
          </b-switch>
          <b-switch
            v-model="write"
          >
            {{ $t('message.share.write_perm') }}
          </b-switch>
          <b-switch
            v-model="listings"
          >
            {{ $t('message.share.list_perm') }}
          </b-switch>
        </b-field>
        <b-field
          :label="$t('message.share.field_label')"
          label-position="on-border"
        >
          <b-taginput
            v-model="tags"
            :placeholder="$t('message.share.field_placeholder')"
          />
        </b-field>
      </section>
      <footer class="modal-card-foot">
        <b-button
          class="is-light"
          @click="$parent.close()"
        >
          {{ $t('message.share.cancel') }}
        </b-button>
        <b-button
          class="is-primary"
        >
          {{ $t('message.share.confirm') }}
        </b-button>
      </footer>
    </div>
  </form>
</template>

<script>
export default {
  name: "Sharing",
  props: ["container"],
  data () {
    return {
      tags: [],
      read: false,
      write: false,
      listings: false,
    };
  },
};
</script>
