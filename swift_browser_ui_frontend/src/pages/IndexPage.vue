<!-- Using the index page as a template for all the error pages as well, to -->
<!-- reduce the need to write things again unnecessarily. Could have made -->
<!-- things into components, but that would break the language support and -->
<!-- make index page development more difficult. -->
<template>
  <div class="indexpage">
    <div>
      <div class="block has-text-centered">
        <a 
          href="#"
          class="center"
        >
          <img
            src="@/assets/logo.svg"
            class="csc-logo"
            :alt="$t('message.cscOrg')"
          >
        </a>
      </div>
      <div class="content has-text-centered">
        <h2 class="title is-4 is-csc-secondary">
          {{ $t("message.program_name") }}
        </h2>
        <p>{{ $t("message.program_description") }}</p>
        <p>{{ $t("message.program_description_step_2") }}</p>
      </div>
      <div class="block">
        <b-message
          v-if="badrequest"
          :title="$t('message.error.BadRequest')"
          type="is-warning"
          has-icon
        >
          {{ $t('message.error.BadRequest_text') }}
        </b-message>
        <b-message
          v-if="unauth"
          :title="$t('message.error.Unauthorized')"
          type="is-warning"
          has-icon
        >
          {{ $t('message.error.Unauthorized_text') }}
        </b-message>
        <b-message
          v-if="forbid"
          :title="$t('message.error.Forbidden')"
          type="is-danger"
          has-icon
        >
          {{ $t('message.error.Forbidden_text') }}
        </b-message>
        <b-message
          v-if="notfound"
          :title="$t('message.error.Notfound')"
          type="is-warning"
          has-icon
        >
          {{ $t('message.error.Notfound_text') }}
        </b-message>
        <b-message
          v-if="uidown"
          :title="$t('message.error.UIdown')"
          type="is-warning"
          has-icon
        >
          {{ $t('message.error.UIdown_text') }}
        </b-message>
        <b-message
          v-if="!idb"
          :title="$t('message.error.idb')"
          type="is-warning"
          has-icon
        >
          {{ $t('message.error.idb_text') }}
        </b-message>
      </div>
      <div
        v-if="!forbid"
        class="block"
      >
        <div 
          v-for="item in $t('message.index.loginmethods')"
          :key="item.msg"
          class="block buttons has-text-centered"
        >
          <b-button
            class="center"
            tag="a"
            type="is-primary"
            :href="item.href"
            :disabled="!idb"
          >
            {{ item.msg }}
          </b-button>
        </div>
      </div>
      <div
        v-if="notindex"
        class="buttons block has-text-centered"
      >
        <b-button
          class="center"
          tag="a"
          type="is-primary"
          href="/"
          :disabled="!idb"
        >
          {{ $t("message.error.frontPage") }}
        </b-button>
      </div>
      <b-field class="locale-changer block center">
        <b-select
          v-model="$i18n.locale"
          placeholder="Language"
          icon="earth"
          expanded
          @input="setCookieLang ()"
        >
          <option
            v-for="lang in langs"
            :key="lang.value"
            :value="lang.value"
          >
            {{ lang.ph }}
          </option>
        </b-select>
      </b-field>
      <div class="block has-text-centered">
        <p>
          {{ $t("message.devel") }}
          <a
            href="https://csc.fi"
            :alt="$t('message.cscOrg')"
          >{{ $t("message.cscOrg") }}</a>
        </p>              
      </div>
    </div>
  </div>
</template>

<script>
import checkIDB from "@/common/idb_support";

export default {
  mounted: function() {
    checkIDB().then(result => this.idb = result);
  },
};
</script>

<style>
html, body {
  height: 100%;
}
.indexpage {
  width: 40%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin: auto;
  align-content: center;
  justify-content: center;
}
.center {
  width: 50%;
  margin: auto;
}
.csc-logo {
  justify-content: center;
}
</style>
