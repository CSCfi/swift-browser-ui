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
      <b-field grouped>
        <b-field
          :label="$t('message.tokens.identLabel')"
          :message="$t('message.tokens.identMessage')"
          expanded
        >
          <b-input
            v-model="newIdentifier"
            name="newIdentifier"
            expanded
          />

          <p
            id="submitButton"
            class="control"
          >
            <button
              v-if="tokenExists(newIdentifier)"
              class="button is-primary"
              disabled
            >
              {{ $t('message.tokens.createToken') }}
            </button>
            <button
              v-else
              class="button is-primary"
              @click="addToken(newIdentifier)"
            >
              {{ $t('message.tokens.createToken') }}
            </button>
          </p>
        </b-field>
      </b-field>
    </div>
    <div
      v-if="latest"
      class="tokenContents"
    >
      <div class="latestTokenRow">
        <span>
          <b>{{ $t('message.tokens.latestToken') }}</b>&nbsp;{{ latest }}&nbsp;
        </span>
        <b-button
          class="copyButton"
          outlined
          icon-left="content-copy"
          @click="copyTokenHex()"
        >
          {{ $t('message.copy') }}
        </b-button>
      </div>
    </div>
    <b-table
      class="tokenContents"
      narrowed
      default-sort="identifier"
      :data="tokens"
      :selected.sync="selected"
      :default-sort-direction="defaultSortDirection"
    >
      <b-table-column
        field="identifier"
        :label="$t('message.tokens.identifier')"
        sortable
      >
        <template #default="props">
          {{ props.row }}
        </template>
      </b-table-column>
      <b-table-column
        field="controls"
      >
        <template #default="props">
          <div class="field has-addons">
            <p class="control">
              <b-button
                v-if="selected==props.row"
                type="is-danger"
                icon-left="delete"
                outlined
                size="is-small"
                inverted
                @click="removeToken(props.row)"
              >
                {{ $t('message.tokens.revoke') }}
              </b-button>
              <b-button
                v-else
                type="is-danger"
                icon-left="delete"
                outlined
                size="is-small"
                @click="removeToken(props.row)"
              >
                {{ $t('message.tokens.revoke') }}
              </b-button>
            </p>
          </div>
        </template>
      </b-table-column>
      <template #empty>
        <span class="emptyContents">
          {{ $t('message.tokens.empty') }}
        </span>
      </template>
    </b-table>
    <c-toasts
      id="token-toasts"
      data-testid="token-toasts"
    />
  </div>
</template>

<script>
import {
  createExtToken,
  listTokens,
  removeToken,
} from "@/common/api";

export default {
  name: "TokensView",
  data () {
    return {
      tokens: [],
      selected: undefined,
      defaultSortDirection: "asc",
      newIdentifier: "",
      latest: undefined,
      copied: false,
    };
  },
  computed: {
    active () {
      return this.$route.params.project;
    },
  },
  beforeMount () {
    this.getTokens();
  },
  methods: {
    getTokens: function () {
      listTokens(this.active).then((ret) => {this.tokens = ret;});
    },
    removeToken: function (identifier) {
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
        this.$buefy.notification.open({
          message: this.$t("message.tokens.copyToken"),
          duration: 3600000,
          type: "is-success",
          queue: false,
        });
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
          document.querySelector("#token-toasts").addToast(
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
@import "@/css/prod.scss";

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
