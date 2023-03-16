<template>
  <c-card class="token-card">
    <c-card-actions
      justify="space-between"
      align="center"
    >
      <h2 class="title is-4 has-text-dark">
        Create API-tokens
      </h2>
      <c-button
        text
        @click="closeTokenModal"
        @keyup.enter="closeTokenModal"
      >
        <c-icon
          :path="mdiClose"
          alt=""
          aria-hidden="true"
        />
        {{ $t("message.share.close") }} <!--add to lg-->
      </c-button>
    </c-card-actions>
    <c-card-content id="create-token">
      <c-text-field
        v-csc-model="newIdentifier"
        name="newIdentifier"
        :label="$t('message.tokens.identLabel')"
      />
      <c-button
        :disabled="tokenExists(newIdentifier)"
        @click="addToken(newIdentifier)"
        @keyup.enter="addToken(newIdentifier)"
      >
        {{ $t('message.tokens.createToken') }}
      </c-button> 
      <c-container v-show="latest">
        <c-row
          align="center"
          justify="space-around"
          gap="10"
        >
          <h3>{{ $t('message.tokens.latestToken') }}</h3>
          <p>{{ latest }}</p>
          <c-button
            size="small"
            @click="copyLatestToken"
            @keyup.enter="copyLatestToken"
          >
            <i
              slot="icon"
              class="mdi mdi-content-copy"
            />
            Copy token
          </c-button>
        </c-row>
      </c-container>
    </c-card-content>
  </c-card>
</template>

<script>
import { mdiClose } from "@mdi/js";
import {
  createExtToken,
  listTokens,
} from "@/common/api";
export default {
  name: "TokenModal",
  data() {
    return {
      tokens: [],
      selected: undefined,
      newIdentifier: "",
      latest: ".................................",
      copied: false,
      mdiClose,
    };
  },
  computed: {
    active() {
      return this.$store.state.active;
    },
  },
  methods: {
    closeTokenModal: function () {
      this.$store.commit("toggleTokenModal", false);
      this.newIdentifier = "";
      this.tokens = [];
      this.selected = undefined;
      //this.latest = undefined;
      this.copied = false;
    },
    getTokens: function () {
      listTokens(this.active).then((ret) => {this.tokens = ret;});
    },
    addToken: function (identifier) {
      createExtToken(
        this.active,
        identifier,
      ).then((ret) => {
        this.latest = ret;
        /*document.querySelector("#add-token-toasts").addToast(
          {
            duration: 3600000,
            type: "success",
            progress: false,
            message: this.$t("message.tokens.copyToken"),
          },
        );*/
        this.getTokens();
      });
    },
    tokenExists: function (identifier) {
      return this.tokens.includes(identifier) ? true : false;
    },
    copyLatestToken: function () {
      if (!this.copied) {
        navigator.clipboard.writeText(
          this.latest,
        ).then(() => {
          this.copied = true;
          /*document.querySelector("#copy-token-toasts").addToast(
            {
              duration: 6000,
              type: "success",
              progress: false,
              message: this.$t("message.tokens.tokenCopied"),
            },
          );
          //like with ShareID copy button:
          //avoid overlapping toasts
          setTimeout(() => { this.copied = false; }, 6000);*/
        });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

.token-card {
  padding: 3rem 2rem 3rem 2rem;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

#create-token >* {
    margin-top: -2rem;
}
</style>