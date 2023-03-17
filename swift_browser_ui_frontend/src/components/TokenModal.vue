<template>
  <c-card class="token-card">
    <c-card-actions
      justify="space-between"
      align="center"
    >
      <h2 class="title is-4 has-text-dark">
        Create API-tokens <!--add to lang-->
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
      <div v-show="latest">
        <c-row
          align="center"
          justify="space-between"
        >
          <p>
            <strong>{{ $t('message.tokens.latestToken') }}</strong>
          </p>
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
        <c-alert type="warning">
          <p>{{ $t('message.tokens.copyToken') }}</p> <!--edit Finnish text-->
        </c-alert>
      </div>
      <c-data-table
        v-show="tokens.length > 0"
        class="tokenContents"
        sort-by="identifier"
        sort-direction="asc"
        :data.prop="tableTokens"
        :headers.prop="headers"
        hide-footer
      />
      <c-toasts
        id="copy-token-toasts"
        data-testid="copy-token-toasts"
      />
    </c-card-content>
  </c-card>
</template>

<script>
import { mdiClose, mdiDelete } from "@mdi/js";
import {
  createExtToken,
  listTokens,
  removeToken,
} from "@/common/api";
export default {
  name: "TokenModal",
  data() {
    return {
      tokens: [],
      selected: undefined,
      newIdentifier: "",
      latest: undefined,
      copied: false,
      mdiClose,
      mdiDelete,
    };
  },
  computed: {
    activeId() {
      return this.$store.state.active.id;
    },
    headers () {
      return [
        {
          key: "identifier",
          value: this.$t("message.tokens.identifier"),
          sortable: this.tokens.length > 1,
        },
        {
          key: "controls",
          width: "10%",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.remove"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.remove"),
                  type: "error",
                  path: mdiDelete,
                  onClick: ({ data: { identifier } }) =>
                    this.deleteToken(identifier.value),
                },
              },
            },
          ],
        },
      ];
    },
    tableTokens () {
      return this.tokens.map(token => {
        return {
          identifier: {
            value: token,
          },
        };
      });
    },
  },
  watch: {
    activeId () {
      this.getTokens(this.activeId);
    },
  },
  methods: {
    closeTokenModal: function () {
      this.$store.commit("toggleTokenModal", false);
      this.newIdentifier = "";
      this.selected = undefined;
      this.latest = undefined;
      this.copied = false;
    },
    getTokens: function () {
      listTokens(this.activeId).then((ret) => {this.tokens = ret;});
    },
    addToken: function (identifier) {
      createExtToken(
        this.activeId,
        identifier,
      ).then((ret) => {
        this.latest = ret;
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
          document.querySelector("#copy-token-toasts").addToast(
            {
              duration: 6000,
              type: "success",
              progress: false,
              message: this.$t("message.tokens.tokenCopied"),
            },
          );
          //like with ShareID copy button:
          //avoid overlapping toasts
          setTimeout(() => { this.copied = false; }, 6000);
        });
      }
    },
    deleteToken: function (identifier) {
      removeToken(
        this.activeId,
        identifier,
      ).then(() => {this.getTokens();});
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

#create-token > c-button {
  margin-top: -2rem;
}

c-text-field {
  margin-top: -1rem;
}

</style>