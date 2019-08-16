<template>

<div class="hero-body">
  <div class="container">
    <div class="columns is-centered">
      <div class="column is-4-desktop is-3-widescreen box" id="login-center">
        <div class="columns is-centered">
          <a href="#">
            <img src="/static/img/csc_logo.svg" :alt="$t('message.cscOrg')">
          </a>
        </div>
        <div>
          <b-message
            v-if="msg"
            :title="msg"
            type="is-warning"
            has-icon
          >{{ msg_text }}</b-message>
        </div>
        <div class="buttons" v-if="!forbid">
          <a class="button is-primary is-fullwidth" href="/login">{{ $t("message.index.logIn") }}</a>
        </div>
        <div class="buttons">
          <a class="button is-primary is-fullwidth" href="/">{{ $t("message.error.frontPage") }}</a>
        </div>
        <b-field class="locale-changer">
          <b-select placeholder="Language" icon="earth"
              v-model="$i18n.locale"
              v-on:input="setCookieLang ()"
              expanded>
            <option v-for="lang in langs" :key="lang.value" :value="lang.value">{{ lang.ph }}</option>
          </b-select>
        </b-field>
        <footer class="footer">
          <div class="content has-text-centered">
            <p>
              <strong>{{ $t("message.program_name") }}</strong> {{ $t("message.devel") }}
              <a href="https://csc.fi" :alt="$t('message.cscOrg')">{{ $t("message.cscOrg") }}</a>
            </p>
        </footer>
      </div>
    </div>
  </div>
</div>

</template>

<script>
export default {
  name: "IndexComp",
  props: [
    "msg",
    "msg_text",
    "forbid",
  ]
}
</script>
