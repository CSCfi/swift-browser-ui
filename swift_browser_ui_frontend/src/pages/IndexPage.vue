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
              :src="require('@/assets/banner_login.png')"
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
                  v-for="item in $t('message.index.loginmethods')"
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
              {{ $t('message.error.Forbidden_text') }}
            </c-card-content>
            <c-card-content v-else-if="notfound">
              {{ $t('message.error.Notfound_text') }}
            </c-card-content>
            <c-card-content v-else-if="uidown">
              {{ $t('message.error.UIdown_text') }}
            </c-card-content>
            <c-card-actions>
              <c-button
                href="/"
                target="_self"
              >
                {{ $t('message.error.frontPage') }}
              </c-button>
            </c-card-actions>
          </c-card>
        </c-container>
      </c-flex>
    </c-row>
    <div id="footer">
      <CFooter/>
    </div>
 </c-main>
</template>

<script>
import checkIDB from "@/common/idb_support";
import CFooter from "@/components/CFooter.vue";

export default {
  mounted: function () {
    checkIDB().then(result => this.idb = result);
  },
  components:{
    CFooter,
  },
};
</script>

<style>
c-main { 
  height: unset; 
  min-height: 100vh 
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

#footer{
  position:fixed;
  bottom:0;
  width:100%;
}

</style>
