<template>
  <c-card
    ref="tokenContainer"
    class="token-card"
    @keydown="handleKeyDown"
  >
    <c-card-actions
      justify="space-between"
      align="center"
    >
      <h2 class="title is-4">
        {{ $t("message.tokens.title") }}
      </h2>
      <c-button
        id="close-token-modal-btn"
        text
        @click="closeTokenModal"
        @keyup.enter="closeTokenModal"
      >
        <c-icon
          :path="mdiClose"
          alt=""
          aria-hidden="true"
        />
        {{ $t("message.close") }}
      </c-button>
    </c-card-actions>
    <c-card-content>
      <c-text-field
        id="token-input"
        v-model="newIdentifier"
        v-csc-control
        name="newIdentifier"
        :label="$t('message.tokens.identLabel')"
      />
      <c-button
        id="create-token-button"
        @click="addToken(newIdentifier)"
        @keyup.enter="addToken(newIdentifier)"
      >
        {{ $t('message.tokens.createToken') }}
      </c-button>
      <c-row
        v-show="latest.token"
        align="start"
        justify="space-between"
      >
        <p>
          <strong>{{ $t('message.tokens.latestToken') }}</strong>
        </p>
        <div id="token">
          <p>{{ latest.token }}</p>
        </div>
        <c-button
          size="small"
          @click="copyLatestToken"
          @keyup.enter="copyLatestToken"
        >
          <i
            slot="icon"
            class="mdi mdi-content-copy"
          />
          {{ $t('message.tokens.copy') }}
        </c-button>
      </c-row>
      <c-alert
        v-show="latest.token"
        type="warning"
      >
        <p>{{ $t('message.tokens.copyWarning') }}</p>
      </c-alert>
      <!-- Footer options needs to be in CamelCase,
      because csc-ui wont recognise it otherwise. -->
      <!-- eslint-disable-->
      <c-data-table
        sort-by="identifier"
        sort-direction="asc"
        :no-data-text="$t('message.tokens.empty')"
        :data.prop="tableTokens"
        :headers.prop="headers"
        :pagination.prop="tokenPagination"
        :footerOptions.prop="footer"
        :hide-footer="tokens.length <= tokensPerPage"
        @click="checkPage"
      />
      <!-- eslint-enable-->
      <c-toasts
        id="token-toasts"
        data-testid="token-toasts"
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
import {
  removeFocusClass,
  addFocusClass,
  moveFocusOutOfModal,
} from "@/common/globalFunctions";

export default {
  name: "TokenModal",
  data() {
    return {
      tokens: [],
      newIdentifier: "",
      latest: {
        token: undefined,
        id: undefined,
      },
      copied: false,
      tokensPerPage: 5,
      mdiClose,
      mdiDelete,
      currentPage: 1,
    };
  },
  computed: {
    visible() {
      return this.$store.state.openTokenModal;
    },
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
                  onClick: ({ data: { identifier }}) =>
                    this.deleteToken(identifier.value),
                  onKeyUp: (e) => {
                    if(e.keyCode === 13) {
                      // Get the row element of item that is to be removed
                      const row = e.target.closest("tr");
                      if (row !== undefined) {
                        const identifierValue = row.children[0]?.innerText;
                        this.deleteToken(identifierValue);
                      }
                    }
                  },
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
    tokenPagination() {
      return {
        itemCount: this.tokens.length,
        itemsPerPage: this.tokensPerPage,
        currentPage: this.currentPage,
      };
    },
    footer() {
      return {
        hideDetails: true,
      };
    },
    prevActiveEl() {
      return this.$store.state.prevActiveEl;
    },
  },
  watch: {
    visible () {
      if (this.visible) this.getTokens(this.activeId);
    },
  },
  methods: {
    checkPage: function(event){
      this.currentPage = event.target.pagination.currentPage;
    },
    closeTokenModal: function () {
      this.currentPage = 1;
      this.$store.commit("toggleTokenModal", false);
      this.newIdentifier = "";
      this.latest = { token: undefined, id: undefined };
      this.copied = false;
      document.querySelector("#token-toasts").removeToast("error-failed");
      document.querySelector("#token-toasts").removeToast("error-in-use");
      document.querySelector("#token-toasts").removeToast("success-copied");
      document.querySelector("#token-toasts").removeToast("success-removed");

      /*
        Prev Active element is a popup menu and it is removed from DOM
        when we click it to open Token Modal.
        Therefore, we need to make its focusable parent
        to be focused instead after we close the modal.
      */
      const prevActiveElParent = document
        .querySelector("[data-testid='support-menu']");
      this.$store.commit("setPreviousActiveEl", prevActiveElParent);
      moveFocusOutOfModal(prevActiveElParent);
    },
    getTokens: function () {
      listTokens(this.activeId).then((ret) => {this.tokens = ret;});
    },
    addToken: function (identifier) {
      if (!this.tokenExists(identifier)) {
        createExtToken(
          this.activeId,
          identifier,
        ).then((ret) => {
          this.latest.token = ret;
          this.latest.id = this.newIdentifier;
          this.newIdentifier = "";
          this.getTokens();
        }).catch(() => {
          document.querySelector("#token-toasts").addToast(
            {
              id: "error-failed",
              type: "error",
              progress: false,
              message: this.$t("message.tokens.creationFailed"),
            },
          );
        });
      }
      else {
        document.querySelector("#token-toasts").addToast(
          {
            id: "error-in-use",
            type: "error",
            progress: false,
            message: this.$t("message.tokens.inUse"),
          },
        );
      }
    },
    tokenExists: function (identifier) {
      return this.tokens.includes(identifier) ? true : false;
    },
    copyLatestToken: function () {
      if (!this.copied) {
        navigator.clipboard.writeText(
          this.latest.token,
        ).then(() => {
          this.copied = true;
          document.querySelector("#token-toasts").addToast(
            {
              id: "success-copied",
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
      ).then(() => {
        if (identifier === this.latest.id) {
          this.latest = {token: undefined, id: undefined};
        }
        document.querySelector("#token-toasts").addToast(
          {
            id: "success-removed",
            type: "success",
            progress: false,
            message: this.$t("message.tokens.tokenRemoved"),
          },
        );
        this.getTokens();
      });

      if(this.tokens.length - 1 == (this.currentPage - 1)
        * this.tokensPerPage) {
        this.currentPage--;
      }
    },
    handleKeyDown: function (e) {
      const eTarget = e.target;
      const shadowDomTarget = eTarget.shadowRoot?.activeElement;

      const first = document.getElementById("close-token-modal-btn");

      // last element is different between with or without token list
      let last = null;

      if (this.tableTokens.length === 0) {
        last = document.getElementById("create-token-button");
      } else {
        const table = this.$refs.tokenContainer.querySelector("c-data-table");
        const removeButtons = table.shadowRoot.querySelectorAll("c-button");
        last = removeButtons[removeButtons.length -1];
      }

      if (e.key === "Tab" && !e.shiftKey &&
        (eTarget === last || (shadowDomTarget === last))
      ) {
        first.tabIndex = "0";
        first.focus();
      } else if (e.key === "Tab" && e.shiftKey) {
        if (eTarget === first) {
          e.preventDefault();
          last.tabIndex = "0";
          last.focus();
          addFocusClass(last);
        } else if (eTarget === last || shadowDomTarget === last) {
          removeFocusClass(last);
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped>

@import "@/css/prod.scss";

.token-card {
  padding: 3rem 2rem;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  max-height: 75vh;
  overflow-y: scroll;
}

#create-token-button {
  width: max-content;
  margin-top: -2rem;
}

#token {
  width: 70%;
  padding: 0rem 0.5rem;
  overflow-wrap: anywhere;
}

@media screen and (max-width: 1366px) {
  #token {
    width: 100%;
    padding: 0.5rem 0;
  }
}

@media screen and (max-width: 992px) {
  .token-card {
    max-height: 60vh;
  }
}

@media screen and (max-width: 576px) {
  .token-card {
    padding: 1.5rem 1rem;
  }
}

</style>
