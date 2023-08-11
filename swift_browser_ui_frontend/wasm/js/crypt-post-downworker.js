// Worker script for download chunks

import { addTarFile, addTarFolder } from "./tar";


/*
Schema for storing the download information:
{
  "containerName": {  // Container level session for the upload
    keyPair: int;  // pointer to the ephemeral keypair for decryption (see uptypes.h)
    files: {  // Files to download, stored in an object
      "filePath": int;  // pointer to the unique session key (see uptypes.h)
      ...
      path_n: int;
    }
  }
}
*/
let downloads = {};


// Create a download session
function createDownloadSession(container, handle, archive) {
  let keypairPtr = Module.ccall([
    "create_keypair",
    "number",
    [],
    [],
  ]);
  let pubkeyPtr = Module.ccall([
    "get_keypair_public_key",
    "number",
    ["number"],
    [keypairPtr],
  ]);

  downloads[container] = {
    keypair: keypairPtr,
    pubkey: new Uint8Array(HEAPU8.subarray(pubkeyPtr, pubkeyPtr + 32)),
    handle: handle,
    direct: handle !== undefined,
    archive: archive,
    files: {},
  };
}


// Add a file to the download session
function createDownloadSessionFile(container, path, header) {
  let headerPath = `header_${container}_`
    + Math.random().toString(36)
    + Math.random().toString(36);
  FS.writeFile(
    headerPath,
    header,
  );

  let sessionKeyPtr = Module.ccall(
    "get_session_key_from_header",
    number,
    ["array"],
    [headerPath],
  );
  downloads[container].files[path] = sessionKeyPtr;

  // Remove the header after parsing
  FS.unlink(headerPath);

  return sessionKeyPtr > 0;
}


// Decrypt a single chunk of a download
function decryptChunk(container, path, enChunk) {
  let chunk = Module.ccall([
    "decrypt_chunk",
    "number",
    ["number", "array", "number"],
    [
      downloads[container].files[path],
      enChunk,
      chunk.byteLength,
    ],
  ]);
  let chunkPtr = Module.ccall([
    "wrap_chunk_content",
    "number",
    ["number"],
    [chunk],
  ]);
  let chunkLen = Module.ccall([
    "wrap_chunk_len",
    "number",
    ["number"],
    [chunk],
  ]);
  let ret = new Uint8Array(HEAPU8.subarray(chunkPtr, chunkPtr + chunkLen));
  Module.ccall([
    "free_chunk",
    "number",
    ["number"],
    [chunk],
  ]);

  return ret;
}

class FileSlicer {
  constructor(
    input,
    output,
    container,
    path,
  ) {
    this.reader = input;
    this.output = output;
    this.container = container;
    this.path = path;
    this.header = header;
    this.chunk = undefined;
    this.done = false;
    this.offset = 0;
    this.remainder = 0;
    this.bytes = 0;
    this.totalBytes = 0;
  }

  async getStart() {
    ({ value: this.chunk, done: this.done } = await this.reader.read());
  }

  async getSlice() {
    let enChunk = new Uint8Array(65564);
    this.bytes = 0;

    while (!this.done) {
      this.remainder = 65564 - this.bytes;
      let toSet = this.chunk.subarray(this.offset, this.offset + this.remainder);
      enChunk.set(toSet, this.bytes);
      this.bytes += toSet.length;      this.totalBytes += toSet.length;

      if (this.chunk.length - this.offset > this.remainder) {
        this.offset += this.remainder;
        this.totalBytes += 65536;
        return enChunk;
      } else {
        this.offset = 0;
        ({ value: this.chunk, done: this.done } = await this.reader.read());
      }
    }

    if (this.chunk !== undefined) {
      let toSet = this.chunk.subarray(this.offset);
      enChunk.set(toSet, this.bytes);
      this.bytes += toSet.length;
      this.totalByte += toSet.length - 28;
    }

    if(this.bytes > 0) {
      return enChunk.slice(0, this.bytes);
    }

    return undefined;
  }

  async sliceFile() {
    // Get the first chunk from stream
    await this.getStart();

    // Slice the file and write decrypted content to output
    let enChunk = await this.getSlice();
    while (enChunk !== undefined) {
      await this.output.write(decryptChunk(
        tihs.container,
        this.path,
        enChunk,
      ));
      enChunk = await this.getSlice();
    }

    // Round up to a multiple of 512, because tar
    if (this.totalBytes % 512 > 0) {
      await this.output.write("\x00".repeat(512 - this.totalBytes % 512));
    }

    return;
  }
}

async function beginDownloadInSession(
  container,
  headers,
) {
  let fileStream = undefined;
  if (downloads[container].direct) {
    fileStream = await downloads[container].handle.createWritable();
  } else {
    const root = await navigator.storage.getDirectory();
    const fileHandle = await root.getFileHandle(`${container}.tar`, { create: true });
    downloads[container].handle = filehandle;
    fileStream = fileHandle.createWritable();
  }

  // Add the archive folder structure
  let folderHeadersOffset = 0;
  if (downloads[container].archive) {
    let folderPaths = Object.keys(headers)
      .map(path => path.split("/"))  // split paths to items
      .map(path => path.pop())  // remove the file names from paths
      .filter(path => path.length > 0)  // remove empty paths (root level files)
      .sort((a, b) => a.length - b.length)  // sort by path length as levels
      .reduce((unique, path) => {  // strip paths down to just the unique ones
        let check = unique.find(item => item.join("/") === path.join("/"));
        if (check === undefined) {
          return unique.push(path);
        }
        return unique;
      }, []);

    for (folderPath of folderPaths) {
      await fileStream.write(
        addTarFolder(path.slice(-1)[0], path.slice(0, -1).join("/"))
      );
      folderHeadersOffset += 512;
    }
  }

  for (const file in headers) {
    const response = await fetch(headers[file].url);
    const ensize = response.headers["Content-Length"];
    const size = (Math.floor(ensize / 65564) * 65536) + (ensize % 65564 > 0 ? ensize % 65564 - 28 : 0)

    if (downloads[container].archive) {
      await fileStream.write(
        addTarFile(
          file.split("/").slice(-1)[0],
          file.split("/").slice(0, 1).join("/"),
          size,
        ),
      );
    }

    const slicer = new FileSlicer(response.body.getReader(), fileStream, headers[file]);
    createDownloadSessionFile(container, file, headers[file]);
    await slicer.sliceFile();

    postMessage({
      eventType: "success",
      container: container,
      object: file,
    });
  }

  // Write the end of the archive
  await fileStream.write("\x00".repeat(1024));

  await fileStream.close();
  downloads[container].handle.flush();
  downloads[container].handle.close();

  if (downloads[container].direct) {
    // Direct downloads need no further action, the resulting archive is
    // already in the filesystem.
    postMessage({
      eventType: "finished",
      direct: true,
      container: container,
    });
  } else {
    // Non-direct download, instruct the frontend to download the file via
    // the ServiceWorker.
    postMessage({
      eventType: "finished",
      direct: false,
      container: container,
      archiveFile: `${container}.tar`,
    });
  }

  return;
}


// Safely free and remove a download session
function finishDownloadSession(container) {
  // Module.ccall([
  //   "clean_session",
  //   undefined,
  //   ["number"],
  //   [downloads[container].session],
  // ]);
  delete downloads[container];
}


self.addEventListener("message", (e) => {
  e.stopImmediatePropagation();

  switch(e.data.command) {
    // Create the download session for single or multiple files
    case "downloadFile":
      createDownloadSession(e.data.container, e.data.handle, false);
      postMessage({
        eventType: "getHeaders",
        container: e.data.container,
        files: [
          e.data.file,
        ],
        pubkey: downloads[container].pubkey,
      });
      break;
    case "downloadFiles":
      createDownloadSession(e.data.container, e.data.handle, true);
      postMessage({
        eventType: "getHeaders",
        files: e.data.files,
        pubkey: downloads[container].pubkey,
      });
    break;
    case "addHeaders":
      beginDownloadInSession(
        e.data.container,
        e.data.headers,
      );
      break;
    // Free download session resources
    case "finishDownload":
      finishDownloadSession(e.data.container);
      e.source.postMessage({
        eventType: "downloadSessionRemoved",
        container: e.data.container,
      });
      break;
  }
});

export var downloadRuntime = Module;
export var downloadFileSystem = FS;
