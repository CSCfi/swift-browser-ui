<template>
  <c-card class="upload-card">
    <div class="upload-form">
      <h3 class="title is-3 has-text-dark">
        {{ $t("message.encrypt.uploadFiles") }}
      </h3>
      <c-card-content>
        <h6 class="title is-6 has-text-dark">
          1. {{ $t("message.encrypt.upload_step1") }}
        </h6>
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.norename") }}
        </p>
        <c-text-field
          v-csc-model="folderName"
          :placeholder="$t('message.container_ops.folderName')"
          name="foldername"
          type="text"
          required
        />
        <b-field
          custom-class="has-text-dark"
          :label="$t('message.tagName')"
          type="is-dark"
        >
          <b-taginput
            v-model="tags"
            class="taginput"
            ellipsis
            maxlength="20"
            has-counter
            rounded
            :placeholder="$t('message.tagPlaceholder')"
            :confirm-keys="taginputConfirmKeys"
            :on-paste-separators="taginputConfirmKeys"
          />
        </b-field>
        <h6 class="title is-6 has-text-dark">
          2. {{ $t("message.encrypt.upload_step2") }}
        </h6>
        <b-upload
          v-model="files"
          multiple
          accept
          drag-drop
          expanded
          class="file is-primary"
        >
          <div class="is-flex is-align-items-center is-justify-content-center">
            <span>{{ $t("message.dropFiles") }}</span>
            <span class="file-cta">
              {{ $t("message.encrypt.dropMsg") }}
            </span>
          </div>
        </b-upload>

        <c-data-table
          :data.prop="dropFiles"
          :headers.prop="headers"
          :no-data-text="$t('message.encrypt.empty')"
          :pagination.prop="paginationOptions"
          :footer-options.prop="footerOptions"
        />
        <p class="info-text is-size-6">
          {{ $t("message.container_ops.createdFolder") }}
          <b>{{ $t("message.container_ops.myResearchProject") }}</b>
        </p>
        <c-link
          :href="`https://my.csc.fi/myProjects/project/${currentProjectID}`"
          underline
          target="_blank"
        >
          {{ $t("message.container_ops.viewProjectMembers") }}
          <i class="mdi mdi-open-in-new" />
        </c-link>
      </c-card-content>
      <c-card-actions justify="space-between">
        <c-button
          outlined
          size="large"
          @click="cancelUpload"
        >
          {{ $t("message.encrypt.cancel") }}
        </c-button>
        <c-button
          size="large"
          :disabled="noUpload"
          @click="beginUpload"
        >
          {{ $t("message.encrypt.normup") }}
        </c-button>
      </c-card-actions>
    </div>
  </c-card>
</template>

<script>
import { getUploadEndpoint } from "@/common/api";
import {
  getHumanReadableSize,
  taginputConfirmKeys,
  truncate,
} from "@/common/conv";

export default {
  name: "UploadView",
  filters: {
    truncate,
  },
  data() {
    return {
      folderName: "",
      tags: [],
      taginputConfirmKeys,
      tooLarge: false,
      noUpload: true,
    };
  },
  computed: {
    res() {
      return this.$store.state.resumableClient;
    },
    active() {
      return this.$store.state.active;
    },
    transfer() {
      return this.$store.state.transfer;
    },
    pubkey() {
      return this.$store.state.pubkey;
    },
    headers() {
      return [
        {
          key: "name",
          value: this.$t("message.encrypt.table.name"),
          width: "30%",
        },
        {
          key: "type",
          value: this.$t("message.encrypt.table.type"),
          width: "15%",
        },
        {
          key: "size",
          value: this.$t("message.encrypt.table.size"),
          width: "10%",
        },
        {
          key: "path",
          value: this.$t("message.encrypt.table.path"),
          width: "30%",
        },
        {
          key: "remove",
          value: null,
          children: [
            {
              value: this.$t("message.remove"),
              component: {
                tag: "c-button",
                params: {
                  text: true,
                  size: "small",
                  title: this.$t("message.remove"),
                  onClick: ({ data }) =>
                    this.$store.commit("eraseDropFile", data["id"]),
                },
              },
            },
          ],
        },
      ];
    },
    dropFiles() {
      return this.$store.state.dropFiles.map(file => {
        return {
          name: { value: file.name || truncate(100) },
          type: { value: file.type },
          size: { value: this.localHumanReadableSize(file.size) },
          path: {
            value:
              (!file.relativePath ? file.name : file.relativePath) ||
              truncate(100),
          },
        };
      });
    },
    files: {
      get() {
        return this.$store.state.dropFiles.message;
      },
      set(value) {
        console.log("value :>> ", value);
        const files = Array.from(value);
        files.forEach(element => {
          this.$store.commit("appendDropFiles", element);
        });
      },
    },
    paginationOptions() {
      return {
        itemCount: this.dropFiles.length,
        itemsPerPage: 20,
        currentPage: 1,
      };
    },
    footerOptions() {
      return {
        hideDetails: true,
        sortable: false,
      };
    },
    currentProjectID() {
      return this.$route.params.project;
    },
  },
  watch: {
    dropFiles: function () {
      this.checkUploadSize();
    },
  },
  methods: {
    setFile: function (item, path) {
      let entry = undefined;
      if (item.isFile) {
        item.file(file => {
          file.relativePath = path + file.name;
          this.$store.commit("appendDropFiles", file);
        });
      } else if (item instanceof File) {
        this.$store.commit("appendDropFiles", item);
      } else if (item.isDirectory) {
        entry = item;
      }
      if ("function" === typeof item.webkitGetAsEntry) {
        entry = item.webkitGetAsEntry();
      }
      // Recursively process items inside a directory
      if (entry && entry.isDirectory) {
        let newPath = path + entry.name + "/";
        let dirReader = entry.createReader();
        let allEntries = [];

        let readEntries = () => {
          dirReader.readEntries(entries => {
            if (entries.length) {
              allEntries = allEntries.concat(entries);
              return readEntries();
            }
            for (let item of allEntries) {
              this.setFile(item, newPath);
            }
          });
        };

        readEntries();
      } else if ("function" === typeof item.getAsFile) {
        item = item.getAsFile();
        if (item instanceof File) {
          item.relativePath = path + item.name;
          this.$store.commit("appendDropFiles", item);
        }
      }
    },
    aBeginUpload: async function (files) {
      // Upload files to the active folder
      let uploadInfo = await getUploadEndpoint(
        this.active.id,
        this.$route.params.owner ? this.$route.params.owner : this.active.id,
        this.folderName,
      );
      this.$store.commit("setUploadInfo", uploadInfo);
      this.res.addFiles(files, undefined);
    },
    beginUpload: function () {
      this.aBeginUpload(this.dropFiles).then(() => {
        this.$buefy.toast.open({
          message: this.$t("message.encrypt.upStart"),
          type: "is-success",
        });
        this.$store.commit("eraseDropFiles");
        this.$store.commit("toggleUploadModal", false);
      });
    },

    checkUploadSize() {
      let size = 0;
      for (let file of this.dropFiles) {
        size += file.size;
      }
      this.tooLarge = size > 1073741824;
    },
    // Make human readable translation functions available in instance
    // namespace
    localHumanReadableSize: function (size) {
      return getHumanReadableSize(size);
    },
    cancelUpload() {
      this.$store.commit("eraseDropFiles");
      this.$store.commit("toggleUploadModal", false);
    },
  },
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

.upload-card {
  width: 64vw;
  padding: 3rem;
  left: 50%;
  margin-top: 50%;
  transform: translate(-50%, -50%);
  height: 85vh;
}

.upload-form {
  overflow-y: scroll;
}

c-card-content {
  padding: 1.5rem 0;
  color: var(--csc-dark-grey);
}

c-text-field {
  width: 70%;
}

.taginput {
  width: 60%;
}

.title.is-6 {
  margin: 0 !important;
}

p.info-text.is-size-6 {
  margin-bottom: -1rem;
}

.is-flex {
  padding: 2rem 0;
  & > span:first-of-type {
    margin-right: 1rem;
  }
}

span.file-cta {
  background-color: transparent !important;
  border: 2px solid var(--csc-primary) !important;
  color: var(--csc-primary) !important;
  font-weight: bold;
}

c-data-table {
  margin-top: -24px;
}

c-card-actions {
  padding: 0;
  margin-top: 1rem;
}
</style>
