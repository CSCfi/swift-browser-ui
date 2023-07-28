<template>
  <c-main>
    <c-toolbar class="relative">
      <c-csc-logo />
      {{ $t('message.program_name') }}
      <c-spacer />
      <LanguageSelector />
    </c-toolbar>
    <c-row v-if="!notindex && idb">
      <c-flex>
        <c-container class="padding">
          <form>
            <c-login-card
              :src="bannerUrl"
            >
              <c-login-card-title>
                {{ $t('message.program_name') }}
              </c-login-card-title>
              <c-login-card-content>
                <p>{{ $t('message.program_description') }}</p>
              </c-login-card-content>
              <c-spacer />
              <c-login-card-actions>
                <c-button
                  v-for="item in $tm('message.index.loginmethods')"
                  :key="item.msg"
                  :disabled="!idb"
                  :href="item.href"
                  target="_self"
                  type="button"
                >
                  <i
                    slot="icon"
                    class="mdi mdi-login"
                  />
                  {{ item.msg }}
                </c-button>
              </c-login-card-actions>
            </c-login-card>
          </form>
        </c-container>
      </c-flex>
    </c-row>
    <c-row v-else>
      <c-flex>
        <c-container>
          <c-card>
            <c-card-title v-if="!idb">
              {{ $t('message.error.idb') }}
            </c-card-title>
            <c-card-title v-else-if="badrequest">
              {{ $t('message.error.BadRequest') }}
            </c-card-title>
            <c-card-title v-else-if="unauth">
              {{ $t('message.error.Unauthorized') }}
            </c-card-title>
            <c-card-title v-else-if="forbid">
              {{ $t('message.error.Forbidden') }}
            </c-card-title>
            <c-card-title v-else-if="notfound">
              {{ $t('message.error.Notfound') }}
            </c-card-title>
            <c-card-title v-else-if="uidown">
              {{ $t('message.error.UIdown') }}
            </c-card-title>
            <c-card-content v-if="!idb">
              {{ $t('message.error.idb_text') }}
            </c-card-content>
            <c-card-content v-else-if="badrequest">
              {{ $t('message.error.BadRequest_text') }}
            </c-card-content>
            <c-card-content v-else-if="unauth">
              {{ $t('message.error.Unauthorized_text') }}
            </c-card-content>
            <c-card-content v-else-if="forbid">
              <div>{{ $t('message.error.Forbidden_text') }}</div>
            </c-card-content>
            <c-card-content v-else-if="notfound">
              {{ $t('message.error.Notfound_text') }}
            </c-card-content>
            <c-card-content v-else-if="uidown">
              <p>
                {{ $t('message.error.UIdown_text1') }}
              </p>
              <p>
                {{ $t('message.error.UIdown_text2') }}
                <c-link
                  :href="$t('message.error.UIdown_link')"
                  underline
                  target="_blank"
                >
                  {{ $t('message.error.UIdown_link_text') }}
                  <i class="mdi mdi-open-in-new" />
                </c-link>
                .
              </p>
            </c-card-content>
            <c-card-actions v-if="unauth">
              <c-button
                href="/login/kill"
                target="_self"
              >
                {{ $t('message.error.login') }}
              </c-button>
            </c-card-actions>
            <c-card-actions v-else-if="forbid || notfound">
              <c-button
                href="/browse"
                target="_self"
              >
                {{ $t('message.error.prevPage') }}
              </c-button>
            </c-card-actions>
          </c-card>
        </c-container>
      </c-flex>
    </c-row>
    <CFooter />
  </c-main>
</template>

<script>
import checkIDB from "@/common/idb_support";
import CFooter from "@/components/CFooter.vue";
import LanguageSelector from "@/components/CLanguageSelector.vue";

export default {
  components:{
    CFooter,
    LanguageSelector,
  },
  mounted: function () {
    checkIDB().then(result => this.idb = result);
  },
  methods: {
    getParams: function(){
      const url = new URL(window.location.href);
      return url.searchParams.get("error");
    },
  },
};
</script>

<style>

c-main {
  height: unset;
  min-height: 100vh;
  justify-content: space-between;
}

c-card {
  margin: 2rem auto;
  max-width: 55rem;
  height: 35rem;
}

c-login-card {
  margin: 2rem auto;
  max-width: 55rem;
  height: 35rem;
}

c-button {
  margin-top: 2rem;
}

</style>
