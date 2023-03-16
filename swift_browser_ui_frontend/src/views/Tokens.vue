<template>
  <div class="contents">
    <div class="tokenContents">
      <section class="section">
        <router-link
          class="back-link"
          :to="{
            name: 'AllFolders',
          }"
        >
          <i class="mdi mdi-chevron-left" />
          {{ $t('message.tokens.back') }}
        </router-link>
      </section>
      <c-row gap="8">
        <c-text-field
          v-model="newIdentifier"
          v-csc-control
          name="newIdentifier"
          :label="$t('message.tokens.identLabel')"
          :hint="$t('message.tokens.identMessage')"
          fit
        />
        <c-button
          :disabled="tokenExists(newIdentifier)"
          @click="addToken(newIdentifier)"
        >
          {{ $t('message.tokens.createToken') }}
        </c-button>
      </c-row>
    </div>
    <div
      v-if="latest"
      class="tokenContents"
    >
      <div class="latestTokenRow">
        <span>
          <b>{{ $t('message.tokens.latestToken') }}</b>&nbsp;{{ latest }}&nbsp;
        </span>
        <c-button
          class="copyButton"
          outlined
          @click="copyTokenHex()"
        >
          <i
            slot="icon"
            class="mdi mdi-content-copy"
          />
          {{ $t('message.copy') }}
        </c-button>
      </div>
    </div>
    <c-data-table
      class="tokenContents"
      sort-by="identifier"
      sort-direction="asc"
      :data.prop="tableTokens"
      :headers.prop="headers"
      :no-data-text="$t('message.tokens.empty')"
      hide-footer
    />
    <c-toasts
      id="add-token-toasts"
      data-testid="add-token-toasts"
      vertical="top"
      horizontal="right"
    />
    <c-toasts
      id="copy-token-toasts"
      data-testid="copy-token-toasts"
    />
  </div>
</template>

<script>
import {
  createExtToken,
  listTokens,
  removeToken,
} from "@/common/api";
import {
  mdiDelete,
} from "@mdi/js";

export default {
  name: "TokensView",
  data () {
    return {
      tokens: [],
      selected: undefined,
      newIdentifier: "",
      latest: undefined,
      copied: false,
    };
  },
  computed: {
    active () {
      return this.$route.params.project;
    },
    headers () {
      return [
        {
          key: "identifier",
          value: this.$t("message.tokens.identifier"),
          sortable: true,
        },
        {
          key: "controls",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.tokens.revoke"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.tokens.revoke"),
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
  beforeMount () {
    this.getTokens();
  },
  methods: {
    getTokens: function () {
      listTokens(this.active).then((ret) => {this.tokens = ret;});
    },
    deleteToken: function (identifier) {
      removeToken(
        this.active,
        identifier,
      ).then(() => {this.getTokens();});
    },
    addToken: function (identifier) {
      createExtToken(
        this.active,
        identifier,
      ).then((ret) => {
        this.latest = ret;
        document.querySelector("#add-token-toasts").addToast(
          {
            duration: 3600000,
            type: "success",
            progress: false,
            message: this.$t("message.tokens.copyToken"),
          },
        );
        this.getTokens();
      });
    },
    tokenExists: function (identifier) {
      return this.tokens.includes(identifier) ? true : false;
    },
    copyTokenHex: function () {
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
  },
};
</script>

<style scoped lang="scss">

.contents{
  font-family: var(--csc-font-family);
}
.tokenContents {
  width: 90%;
  margin-left: 5%;
  margin-right: 5%;
}
.emptyContents {
  width: 100%;
  text-align: center;
  margin-top: 5%;
  margin-bottom: 5%;
}
.latestTokenRow {
  display: flex;
  align-items: center;
  justify-content: left;
}
.copyButton {
  margin-left: 1%;
}
.back-link {
  display: flex;
  padding-bottom: .5rem;
  color: $csc-primary;
  font-weight: 600;
  align-items: center;

  & .mdi {
    font-size: 2rem;
  }
}
</style>
