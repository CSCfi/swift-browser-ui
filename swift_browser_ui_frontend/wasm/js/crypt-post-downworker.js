// Worker script for download chunks

import { addTarFile, addTarFolder } from "./tar";
import { checkPollutingName } from "./nameCheck";

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
// Text encoder for quickly encoding tar headers
let enc = new TextEncoder();
let libinitDone = false;
let downProgressInterval = undefined;
let totalDone = 0;
let totalToDo = 0;
let aborted = false;

/*
This script supports being loaded both as a ServiceWorker and an ordinary
worker. The former is to provide support for Firefox and Safari, which only
implement an OPFS version of File System API for security reasons.
Additionally, Firefox <= 110 (e.g. Firefox ESR), lacks any form of
File System API altogether.

SerivceWorker based approach streams the file through ServiceWorker, into
a specific file download. This is a tad slower, since multiple files can't
be downloaded / decrypted in parallel due to the lack of random access,
but is reasonably performant anyways.

OPFS based version might not be worth it in real world use, since it needs
intermediary storage and the ServiceWorker doesn't.
*/


// Example: https://devenv:8443/file/test-container/examplefile.txt.c4gh
const fileUrl = new RegExp("/file/[^/]*/.*$");
// Example: https://devenv:8443/archive/test-container.tar
const archiveUrl = new RegExp("/archive/[^/]*\\.tar$");
const fileUrlStart = new RegExp("/file/[^/]*/");

if (inServiceWorker) {
  self.addEventListener("install", (event) => {
    event.waitUntil(waitAsm());
  });
  self.addEventListener("activate", (event) => {
    event.waitUntil(self.clients.claim());
  });
}

// Create a download session
function createDownloadSession(container, handle, archive) {
  let keypairPtr = Module.ccall(
    "create_keypair",
    "number",
    [],
    [],
  );

  let pubkeyPtr = Module.ccall(
    "get_keypair_public_key",
    "number",
    ["number"],
    [keypairPtr],
  );

  downloads[container] = {
    keypair: keypairPtr,
    pubkey: new Uint8Array(HEAPU8.subarray(pubkeyPtr, pubkeyPtr + 32)),
    handle: handle,
    direct: !inServiceWorker,
    archive: archive,
    files: {},
  };
}


// Add a file to the download session
function createDownloadSessionFile(container, path, header, url) {
  if (checkPollutingName(path)) return;

  let headerPath = `header_${container}_`
    + Math.random().toString(36)
    + Math.random().toString(36);
  FS.writeFile(
    headerPath,
    header,
  );

  let sessionKeyPtr = Module.ccall(
    "get_session_key_from_header",
    "number",
    ["number", "string"],
    [downloads[container].keypair, headerPath],
  );

  downloads[container].files[path] = {
    key: sessionKeyPtr,
    url: url,
  };

  // Remove the header after parsing
  FS.unlink(headerPath);

  // Cache the header if no suitable key couldn't be found
  if (sessionKeyPtr <= 0) {
    downloads[container].files[path].header = header;
  }

  return sessionKeyPtr > 0;
}


// Decrypt a single chunk of a download
function decryptChunk(container, path, enChunk) {
  let chunk = Module.ccall(
    "decrypt_chunk",
    "number",
    ["number", "array", "number"],
    [
      downloads[container].files[path].key,
      enChunk,
      enChunk.length,
    ],
  );
  let chunkPtr = Module.ccall(
    "wrap_chunk_content",
    "number",
    ["number"],
    [chunk],
  );
  let chunkLen = Module.ccall(
    "wrap_chunk_len",
    "number",
    ["number"],
    [chunk],
  );
  // We need to clone the view to a new typed array, otherwise it'll get
  // stale on return
  let ret = new Uint8Array(HEAPU8.subarray(chunkPtr, chunkPtr + chunkLen));
  totalDone += chunkLen;
  Module.ccall(
    "free_chunk_nobuf",
    "number",
    ["number"],
    [chunk],
  );

  return ret;
}

function getFileSize(response, key) {
  // Use encrypted size as the total file size if the file can't be decrypted
  const ensize = parseInt(response.headers.get("Content-Length"));
  return key !=0 ?
    (Math.floor(ensize / 65564) * 65536) +
    (ensize % 65564 > 0 ? ensize % 65564 - 28 : 0) :
    ensize;
}

function startProgressInterval() {
  const interval = setInterval(() => {
    postMessage({
      eventType: "progress",
      progress: totalDone / totalToDo < 1 ? totalDone / totalToDo : 1,
    });
  }, 250);
  return interval;
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

  setController(controller) {
    this.output = controller;
  }

  async getSlice() {
    let enChunk = new Uint8Array(65564);
    this.bytes = 0;

    while (!this.done) {
      this.remainder = 65564 - this.bytes;
      let toSet = this.chunk.subarray(this.offset, this.offset + this.remainder);
      enChunk.set(toSet, this.bytes);
      this.bytes += toSet.length;

      if (this.chunk.length - this.offset > this.remainder) {
        this.offset += this.remainder;
        this.totalBytes += 65536;
        return enChunk;
      } else {
        this.offset = 0;
        ({ value: this.chunk, done: this.done } = await this.reader.read());
      }
    }

    if(this.bytes > 0) {
      this.totalBytes += this.bytes - 28;
      return enChunk.slice(0, this.bytes);
    }

    return undefined;
  }

  async padFile() {
    if (this.totalBytes % 512 > 0 && downloads[this.container].archive) {
      let padding = "\x00".repeat(512 - this.totalBytes % 512);
      if (this.output instanceof WritableStream) {
        await this.output.write(enc.encode(padding));
      } else {
        this.output.enqueue(enc.encode(padding));
      }
    }
  }

  async concatFile() {
    // If the file can't be decrypted, add the header and concat the encrypted
    // file to the stream
    if (this.output instanceof WritableStream) {
      await this.output.write(downloads[this.container].files[this.path].header);
    } else {
      this.output.enqueue(downloads[this.container].files[this.path].header);
    }

    await this.getStart();

    while (!this.done) {
      if (this.output instanceof WritableStream) {
        await this.output.write(this.chunk);
      } else {
        this.output.enqueue(downloads[this.contaier].files[this.path].header);
      }
      this.totalBytes += this.chunk.length;
      ({ value: this.chunk, done: this.done } = await this.reader.read());
    }

    // Round up to a multiple of 512, because tar
    await this.padFile();

    return;
  }

  async sliceFile() {
    // Get the first chunk from stream
    await this.getStart();

    // Slice the file and write decrypted content to output
    let enChunk = await this.getSlice();
    while (enChunk !== undefined) {
      if (this.output instanceof WritableStream) {
        // Write the decrypted contents directly in the file stream if
        // downloading to File System
        await this.output.write(decryptChunk(
          this.container,
          this.path,
          enChunk,
        ));
      } else {
        // Otherwise queue to the streamController since we're using a
        // ServiceWorker for downloading
        while(this.output.desiredSize <= 0) {
          await timeout(10);
        }
        this.output.enqueue(decryptChunk(
          this.container,
          this.path,
          enChunk,
        ));
      }
      enChunk = await this.getSlice();
    }

    // Round up to a multiple of 512, because tar
    await this.padFile();

    // Free the session key
    Module.ccall(
      "free_crypt4gh_session_key",
      undefined,
      ["number"],
      [downloads[this.container].files[this.path].key],
    );
    return true;
  }
}

function clear() {
  if (downProgressInterval) {
    clearInterval(downProgressInterval);
    downProgressInterval = undefined;
  }
  totalDone = 0;
  totalToDo = 0;
}

function abortDownloads(direct) {
  if (direct) {
    postMessage({
      eventType: "error",
    });
  } else {
    self.clients.matchAll().then(clients => {
      clients.forEach(client =>
        client.postMessage({
          eventType: "error",
        }));
    });
  }
  clear();
  aborted = true;
  for (let container in downloads) {
    finishDownloadSession(container);
  }
}


// Safely free and remove a download session
function finishDownloadSession(container) {
  Module.ccall(
    "free_keypair",
    undefined,
    ["number"],
    [downloads[container].keypair],
  );
  delete downloads[container];
}


async function addSessionFiles(
  container,
  headers,
) {
  let undecryptable = false;

  for (const file in headers) {
    if (!createDownloadSessionFile(container, file, headers[file].header, headers[file].url)) {
      undecryptable = true;
    }
  }

  return undecryptable;
}


async function beginDownloadInSession(
  container,
) {
  aborted = false; //reset with download start

  let fileHandle = downloads[container].handle;
  let fileStream;
  if (downloads[container].direct) {
    fileStream = await fileHandle.createWritable();
  } else {
    fileStream = fileHandle;
  }

  // Add the archive folder structure
  if (downloads[container].archive) {
    let folderPaths = Object.keys(downloads[container].files)
      .map(path => path.split("/"))  // split paths to items
      .map(path => path.slice(0, -1))  // remove the file names from paths
      .filter(path => path.length > 0)  // remove empty paths (root level files)
      .sort((a, b) => a.length - b.length)  // sort by path length as levels
      .reduce((unique, path) => {  // strip paths down to just the unique ones
        let check = unique.find(item => item.join("/") === path.join("/"));
        if (check === undefined) {
          unique.push(path);
        }
        return unique;
      }, []);

    for (const path of folderPaths) {
      if (downloads[container].direct) {
        await fileStream.write(
          addTarFolder(path),
        );
      } else {
        fileStream.enqueue(addTarFolder(path));
      }
    }
  }

  if (downloads[container].direct) {
  //get total download size and periodically report download progress
    for (const file in downloads[container].files) {
      const res = await fetch(downloads[container].files[file].url);
      totalToDo += getFileSize(res, downloads[container].files[file].key);
    }
    if (!downProgressInterval) {
      downProgressInterval = startProgressInterval();
    }
  }

  for (const file in downloads[container].files) {
    if (inServiceWorker) {
      self.clients.matchAll().then(clients => {
        clients.forEach(client =>
          client.postMessage({
            eventType: "downloadProgressing",
            container: container,
          }));
      });
    }

    const response = await fetch(downloads[container].files[file].url);
    let path = file.replace(".c4gh", "");

    if (downloads[container].archive) {
      const size = getFileSize(response, downloads[container].files[file].key);

      let fileHeader = addTarFile(
        downloads[container].files[file].key != 0 ? path : file,
        size,
      );

      if (downloads[container].direct) {
        await fileStream.write(fileHeader);
      } else {
        fileStream.enqueue(fileHeader);
      }
    }

    const slicer = new FileSlicer(
      response.body.getReader(),
      fileStream,
      container,
      file);

    let res;
    if (downloads[container].files[file].key <= 0) {
      res = await slicer.concatFile().catch(() => {
        return false;
      });
    } else {
      res = await slicer.sliceFile().catch(() => {
        return false;
      });
      if (!res) {
        if (!aborted) abortDownloads(!inServiceWorker);
        return;
      }
    }
  }

  if (downloads[container].archive) {
    // Write the end of the archive
    if (downloads[container].direct) {
      await fileStream.write(enc.encode("\x00".repeat(1024)));
    } else {
      fileStream.enqueue(enc.encode("\x00".repeat(1024)));
    }
  }

  // Sync the file if downloading directly into file, otherwise finish
  // the fetch request.
  if (downloads[container].direct) {
    await fileStream.close();
  // downloads[container].handle.flush();
  // downloads[container].handle.close();
  } else {
    fileStream.close();
  }

  if (downloads[container].direct) {
  // Direct downloads need no further action, the resulting archive is
  // already in the filesystem.
    postMessage({
      eventType: "finished",
      direct: true,
      container: container,
    });
  } else {
  // Inform download with service worker finished
    self.clients.matchAll().then(clients => {
      clients.forEach(client =>
        client.postMessage({
          eventType: "downloadProgressFinished",
          container: container,
        }));
    });
  }
  finishDownloadSession(container);
  return;
}

if (inServiceWorker) {
  // Add listener for fetch events
  self.addEventListener("fetch", (e) => {
    const url = new URL(e.request.url);

    let fileName;
    let containerName;

    if (fileUrl.test(url.pathname)) {
      fileName = url.pathname.replace(fileUrlStart, "");
      containerName = url.pathname.replace("/file/", "").replace(fileName, "").replace("/", "");
    } else if (archiveUrl.test(url.pathname)) {
      fileName = url.pathname.replace("/archive/", "");
      containerName = fileName.replace(/\.tar$/, "");
    } else {
      return;
    }

    // Fix URL safe contents
    fileName = decodeURIComponent(fileName);
    containerName = decodeURIComponent(containerName);

    if (checkPollutingName(containerName)) return;

    if (fileUrl.test(url.pathname) || archiveUrl.test(url.pathname)) {
      let streamController;
      const stream = new ReadableStream({
        start(controller) {
          streamController = controller;
        },
      });
      const response = new Response(stream);
      response.headers.append(
        "Content-Disposition",
        "attachment; filename=\"" + fileName.replace(".c4gh", "") + "\"",
      );

      // Map the streamController as the stream for the download
      downloads[containerName].handle = streamController;

      // Start the decrypt slicer and respond, tell worker to stay open until
      // stream is consumed
      e.respondWith((() => {
        e.waitUntil(beginDownloadInSession(containerName));
        return response;
      })());
    }
  });
}

self.addEventListener("message", async (e) => {
  // Sanity check container name
  if (checkPollutingName(e.data.container)) return;

  switch(e.data.command) {
    case "downloadFile":
      if (inServiceWorker) {
        while (!libinitDone) {
          await timeout(250);
        }
        if (libinitDone) {
          createDownloadSession(e.data.container, undefined, false);
          e.source.postMessage({
            eventType: "getHeaders",
            container: e.data.container,
            files: [
              e.data.file,
            ],
            pubkey: downloads[e.data.container].pubkey,
            owner: e.data.owner,
            ownerName: e.data.ownerName,
          });
        }
      } else {
        createDownloadSession(e.data.container, e.data.handle, false);
        postMessage({
          eventType: "getHeaders",
          container: e.data.container,
          files: [
            e.data.file,
          ],
          pubkey: downloads[e.data.container].pubkey,
          owner: e.data.owner,
          ownerName: e.data.ownerName,
        });
      }
      break;
    case "downloadFiles":
      if (inServiceWorker) {
        while (!libinitDone) {
          await timeout(250);
        }
        if (libinitDone) {
          createDownloadSession(e.data.container, undefined, true);
          e.source.postMessage({
            eventType: "getHeaders",
            container: e.data.container,
            files: e.data.files,
            pubkey: downloads[e.data.container].pubkey,
            owner: e.data.owner,
            ownerName: e.data.ownerName,
          });
        }
      } else {
        createDownloadSession(e.data.container, e.data.handle, true);
        postMessage({
          eventType: "getHeaders",
          container: e.data.container,
          files: e.data.files,
          pubkey: downloads[e.data.container].pubkey,
          owner: e.data.owner,
          ownerName: e.data.ownerName,
        });
      }
      break;
    case "addHeaders":
      addSessionFiles(e.data.container, e.data.headers).then(ret => {
        if (ret && inServiceWorker) {
          e.source.postMessage({
            eventType: "notDecryptable",
            container: e.data.container,
          });
        } else if (ret) {
          postMessage({
            eventType: "notDecryptable",
            container: e.data.container,
          });
        }
      });
      if (inServiceWorker) {
        e.source.postMessage({
          eventType: "downloadStarted",
          container: e.data.container,
          archive: downloads[e.data.container].archive,
          path: downloads[e.data.container].archive ? undefined
            : Object.keys(e.data.headers)[0],
        });
      } else {
        beginDownloadInSession(e.data.container);
        postMessage({
          eventType: "downloadStarted",
          container: e.data.container,
        });
      }
      break;
    case "keepDownloadProgressing":
      break;
    case "clear":
      clear();
      break;
  }
});

waitAsm().then(() => {
  Module.ccall("libinit", undefined, undefined, undefined);
  libinitDone = true;
});

export var downloadRuntime = Module;
export var downloadFileSystem = FS;
