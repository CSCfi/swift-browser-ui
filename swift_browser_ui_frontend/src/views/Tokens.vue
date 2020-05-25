<template>
  <div class="contents">
    <div class="tokenContents">
      <b-field grouped>
        <b-field
          horizontal
          :label="$t('message.tokens.identLabel')"
          :message="$t('message.tokens.identMessage')"
          expanded
        >
          <b-input
            v-model="newIdentifier"
            name="newIdentifier"
            expanded
          />
        </b-field>
        <b-field>
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
      <b>Latest token: </b> {{ latest }}
    </div>
    <b-table
      class="tokenContents"
      narrowed
      default-sort="identifier"
      :data="tokens"
      :selected.sync="selected"
      :default-sort-direction="defaultSortDirection"
    >
      <template slot-scope="props">
        <b-table-column
          field="identifier"
          :label="$t('message.tokens.identifier')"
          sortable
        >
          {{ props.row }}
        </b-table-column>
        <b-table-column
          field="controls"
          label=""
        >
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
        </b-table-column>
      </template>
      <template slot="empty">
        <span class="emptyContents">
          {{ $t('message.tokens.empty') }}
        </span>
      </template>
    </b-table>
  </div>
</template>

<style scoped>
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
</style>

<script>
import {
  createExtToken,
  listTokens,
  removeToken,
} from "@/common/api";

export default {
  name: "Tokens",
  data () {
    return {
      tokens: [],
      selected: undefined,
      defaultSortDirection: "asc",
      newIdentifier: "",
      latest: undefined,
    };
  },
  beforeMount () {
    this.getTokens();
  },
  methods: {
    getTokens: function () {
      listTokens().then((ret) => {this.tokens = ret;});
    },
    removeToken: function (identifier) {
      removeToken(identifier).then(() => {this.getTokens();});
    },
    addToken: function (identifier) {
      createExtToken(identifier).then((ret) => {
        this.latest = ret;
        this.$buefy.toast.open({
          message: "Copy the token displayed below identifier field",
          type: "is-success",
        });
        this.getTokens();
      });
    },
    tokenExists: function (identifier) {
      return this.tokens.includes(identifier) ? true : false;
    },
  },
};
</script>
