<template>
  <c-card
    ref="apiKeyContainer"
    class="api-key-card"
    @keydown="handleKeyDown"
  >
    <c-card-actions
      justify="space-between"
      align="center"
    >
      <h2 class="title is-4">
        {{ $t("message.apiKeys.title") }}
      </h2>
      <c-button
        id="close-api-key-modal-btn"
        text
        @click="closeModal(false)"
        @keyup.enter="closeModal(true)"
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
      <p>{{ $t("message.apiKeys.identHint") }}</p>
      <c-text-field
        id="api-key-input"
        v-model="newIdentifier"
        v-csc-control
        name="newIdentifier"
        :label="$t('message.apiKeys.identLabel')"
        :valid="!inputError"
        :validation="inputError"
        @changeValue="inputError = ''"
      />
      <c-button
        id="create-api-key-button"
        @click="addAPIKey(newIdentifier)"
        @keyup.enter="addAPIKey(newIdentifier)"
      >
        {{ $t("message.apiKeys.create") }}
      </c-button>
      <c-row
        v-show="latest.apiKey"
        align="start"
        justify="space-between"
      >
        <p>
          <strong>{{ $t("message.apiKeys.latest") }}</strong>
        </p>
        <div id="api-key">
          <p>{{ latest.apiKey }}</p>
        </div>
        <c-button
          size="small"
          @click="copyLatest"
          @keyup.enter="copyLatest"
        >
          <i
            slot="icon"
            class="mdi mdi-content-copy"
          />
          {{ $t('message.apiKeys.copy') }}
        </c-button>
      </c-row>
      <c-alert
        v-show="latest.apiKey"
        type="warning"
      >
        <p>{{ $t('message.apiKeys.copyWarning') }}</p>
      </c-alert>
      <!-- Footer options needs to be in CamelCase,
      because csc-ui wont recognise it otherwise. -->
      <c-data-table
        sort-by="identifier"
        sort-direction="asc"
        :no-data-text="$t('message.apiKeys.empty')"
        :data.prop="tableAPIKeys"
        :headers.prop="headers"
        :pagination.prop="apiKeyPagination"
        :footerOptions.prop="footer"
        :hide-footer="apiKeys.length <= apiKeysPerPage"
        @click="checkPage"
      />
      <c-toasts
        id="api-key-toasts"
        data-testid="api-key-toasts"
      />
    </c-card-content>
  </c-card>
</template>

<script>
import { mdiClose, mdiDelete } from "@mdi/js";
import {
  createAPIKey,
  listAPIKeys,
  removeAPIKey,
} from "@/common/api";
import {
  addFocusClass,
  removeFocusClass,
  moveFocusOutOfModal,
} from "@/common/keyboardNavigation";
export default {
  name: "APIKeyModal",
  data() {
    return {
      apiKeys: [],
      newIdentifier: "",
      latest: {
        apiKey: undefined,
        id: undefined,
      },
      copied: false,
      apiKeysPerPage: 5,
      mdiClose,
      mdiDelete,
      currentPage: 1,
      inputError: "",
    };
  },
  computed: {
    visible() {
      return this.$store.state.openAPIKeyModal;
    },
    activeId() {
      return this.$store.state.active.id;
    },
    headers () {
      return [
        {
          key: "identifier",
          value: this.$t("message.apiKeys.identifier"),
          sortable: this.apiKeys.length > 1,
        },
        {
          key: "controls",
          width: "10%",
          value: null,
          sortable: false,
          children: [
            {
              value: this.$t("message.delete"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.delete"),
                  type: "error",
                  path: mdiDelete,
                  onClick: ({ data: { identifier }}) =>
                    this.deleteAPIKey(identifier.value),
                  onKeyUp: (e) => {
                    if(e.keyCode === 13) {
                      // Get the row element of item that is to be removed
                      const row = e.target.closest("tr");
                      if (row !== undefined) {
                        const identifierValue = row.children[0]?.innerText;
                        this.deleteAPIKey(identifierValue);
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
    tableAPIKeys () {
      return this.apiKeys.map(apiKey => {
        return {
          identifier: {
            value: apiKey,
          },
        };
      });
    },
    apiKeyPagination() {
      return {
        itemCount: this.apiKeys.length,
        itemsPerPage: this.apiKeysPerPage,
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
      if (this.visible) this.getAPIKeys(this.activeId);
    },
  },
  methods: {
    checkPage: function(event){
      this.currentPage = event.target.pagination.currentPage;
    },
    closeModal: function (addFocus) {
      this.currentPage = 1;
      this.$store.commit("toggleAPIKeyModal", false);
      this.newIdentifier = "";
      this.latest = { apiKey: undefined, id: undefined };
      this.copied = false;
      this.inputError = "";
      document.querySelector("#api-key-toasts").removeToast("error-failed");
      document.querySelector("#api-key-toasts").removeToast("error-in-use");
      document.querySelector("#api-key-toasts").removeToast("success-copied");
      document.querySelector("#api-key-toasts").removeToast("success-removed");

      /*
        Prev Active element is a popup menu and it is removed from DOM
        when we click it to open the modal.
        Therefore, we need to make its focusable parent
        to be focused instead after we close the modal.
      */
      const prevActiveElParent = document
        .querySelector("[data-testid='support-menu']");
      moveFocusOutOfModal(prevActiveElParent, true, addFocus);
    },
    getAPIKeys: function () {
      listAPIKeys(this.activeId).then((ret) => {this.apiKeys = ret;});
    },
    addAPIKey: function (identifier) {
      if (!identifier) {
        this.inputError = this.$t("message.apiKeys.required");
      }
      else if (this.apiKeyExists(identifier)) {
        this.inputError = this.$t("message.apiKeys.inUse");
      }
      else {
        createAPIKey(
          this.activeId,
          identifier,
        ).then((ret) => {
          this.latest.apiKey = ret;
          this.latest.id = this.newIdentifier;
          this.newIdentifier = "";
          this.getAPIKeys();
        }).catch(() => {
          document.querySelector("#api-key-toasts").addToast(
            {
              id: "error-failed",
              type: "error",
              progress: false,
              message: this.$t("message.apiKeys.creationFailed"),
            },
          );
        });
      }
    },
    apiKeyExists: function (identifier) {
      return this.apiKeys.includes(identifier) ? true : false;
    },
    copyLatest: function () {
      if (!this.copied) {
        navigator.clipboard.writeText(
          this.latest.apiKey,
        ).then(() => {
          this.copied = true;
          document.querySelector("#api-key-toasts").addToast(
            {
              id: "success-copied",
              type: "success",
              progress: false,
              message: this.$t("message.apiKeys.copied"),
            },
          );
          //like with ShareID copy button:
          //avoid overlapping toasts
          setTimeout(() => { this.copied = false; }, 6000);
        });
      }
    },
    deleteAPIKey: function (identifier) {
      removeAPIKey(
        this.activeId,
        identifier,
      ).then(() => {
        if (identifier === this.latest.id) {
          this.latest = {apiKey: undefined, id: undefined};
        }
        document.querySelector("#api-key-toasts").addToast(
          {
            id: "success-removed",
            type: "success",
            progress: false,
            message: this.$t("message.apiKeys.removed"),
          },
        );
        this.getAPIKeys();
      });

      if(this.apiKeys.length - 1 == (this.currentPage - 1)
        * this.apiKeysPerPage) {
        this.currentPage--;
      }
    },
    handleKeyDown: function (e) {
      const eTarget = e.target;
      const shadowDomTarget = eTarget.shadowRoot?.activeElement;

      const first = document.getElementById("close-api-key-modal-btn");

      // last element is different between with or without API key list
      let last = null;

      if (this.tableAPIKeys.length === 0) {
        last = document.getElementById("create-api-key-button");
      } else {
        const table = this.$refs.apiKeyContainer.querySelector("c-data-table");
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

<style scoped>

.api-key-card {
  padding: 3rem 2rem;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  max-height: 75vh;
  overflow-y: scroll;
}

#create-api-key-button {
  width: max-content;
  margin-top: -1rem;
}

#api-key {
  width: 70%;
  padding: 0rem 0.5rem;
  overflow-wrap: anywhere;
}

@media screen and (max-width: 1366px) {
  #api-key {
    width: 100%;
    padding: 0.5rem 0;
  }
}

@media screen and (max-width: 992px) {
  .api-key-card {
    max-height: 60vh;
  }
}

@media screen and (max-width: 576px) {
  .api-key-card {
    padding: 1.5rem 1rem;
  }
}

</style>
