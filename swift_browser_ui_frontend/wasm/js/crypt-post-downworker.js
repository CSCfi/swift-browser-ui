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
let cancelled = false;

// Use a 50 MiB segment when downloading
const DOWNLOAD_SEGMENT_SIZE = 1024 * 1024 * 50;
// Don't segment downloads under 250 MiB
const DOWNLOAD_MAX_NONSEGMENTED_SIZE = 1024 * 1024 * 250;

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


// Example: https://devenv:8443/file/session-id/test-container/examplefile.txt.c4gh
const fileUrl = new RegExp("/file/[^/]*/[^/]*/.*$");
// Example: https://devenv:8443/archive/session-id/test-container.tar
const archiveUrl = new RegExp("/archive/[^/]*/[^/]*\\.tar$");
const fileUrlStart = new RegExp("/file/[^/]*/[^/]*/");
const archiveUrlStart = new RegExp("/archive/[^/]*/");

if (inServiceWorker) {
  self.addEventListener("install", (event) => {
    event.waitUntil(waitAsm());
  });
  self.addEventListener("activate", (event) => {
    event.waitUntil(self.clients.claim());
  });

}

// Create a download session
function createDownloadSession(id, container, handle, archive) {
  aborted = false; //reset
  cancelled = false;

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

  downloads[id] = {
    keypair: keypairPtr,
    pubkey: new Uint8Array(HEAPU8.subarray(pubkeyPtr, pubkeyPtr + 32)),
    handle: handle,
    direct: !inServiceWorker,
    archive: archive,
    container: container,
    files: {},
  };
}

function getFileSize(size, key) {
  // Use encrypted size as the total file size if the file can't be decrypted
  return key !=0 ?
    (Math.floor(size / 65564) * 65536) +
    (size % 65564 > 0 ? size % 65564 - 28 : 0) :
    size;
}

// Add a file to the download session
function createDownloadSessionFile(id, container, path, header, url, size) {
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
    [downloads[id].keypair, headerPath],
  );

  downloads[id].files[path] = {
    key: sessionKeyPtr,
    url: url,
    size: getFileSize(size, sessionKeyPtr),
    realsize: getFileSize(size, 0),
  };

  // Remove the header after parsing
  FS.unlink(headerPath);

  // Cache the header if no suitable key couldn't be found
  if (sessionKeyPtr <= 0) {
    downloads[id].files[path].header = header;
  }

  return sessionKeyPtr > 0;
}


// Decrypt a single chunk of a download
function decryptChunk(id, path, enChunk) {
  let chunk = Module.ccall(
    "decrypt_chunk",
    "number",
    ["number", "array", "number"],
    [
      downloads[id].files[path].key,
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
  // Don't clone the view, as async writes can't happen in parallel.
  // ServiceWorker download takes care of cloning as needed.
  let ret = HEAPU8.subarray(chunkPtr, chunkPtr + chunkLen);
  totalDone += chunkLen;

  return ret;
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
    output,
    id,
    path,
  ) {
    this.reader = undefined;
    this.output = output;
    this.id = id,
    this.path = path;
    this.chunk = undefined;
    this.done = false;
    this.offset = 0;
    this.remainder = 0;
    this.bytes = 0;
    this.totalBytes = 0;
    this.enChunkBuf = new Uint8Array(65564);

    // Cache total file size to properly iterate through responses
    // as fetch bodies larger than 4 GiB can cause issues with memory
    // management.
    this.segmentOffset = 0;
  }

  async getNextSegment() {
    let resp;

    // Don't separate smaller downloads (< 250 MiB) into ranges
    if (downloads[this.id].files[this.path].realsize < DOWNLOAD_MAX_NONSEGMENTED_SIZE) {
      resp = await fetch(
        downloads[this.id].files[this.path].url,
      ).catch(() => {});
      this.segmentOffset += DOWNLOAD_MAX_NONSEGMENTED_SIZE;
      this.reader = resp.body.getReader();
      return;
    }

    let end = this.segmentOffset + DOWNLOAD_SEGMENT_SIZE - 1;
    let range = `bytes=${this.segmentOffset}-${end}`;
    resp = await fetch(
      downloads[this.id].files[this.path].url,
      {
        headers: {
          "Range": range,
        },
      },
    ).catch(e => {
      console.log(e);
    });
    this.segmentOffset += DOWNLOAD_SEGMENT_SIZE;
    this.reader = resp.body.getReader();
  }

  async getStart() {
    await this.getNextSegment();
    ({ value: this.chunk, done: this.done } = await this.reader.read());
  }

  setController(controller) {
    this.output = controller;
  }

  async getSlice() {
    this.bytes = 0;

    while (!this.done) {
      this.remainder = 65564 - this.bytes;
      this.enChunkBuf.set(this.chunk.subarray(this.offset, this.offset + this.remainder), this.bytes);
      this.bytes += this.chunk.subarray(this.offset, this.offset + this.remainder).length;

      if (this.chunk.length - this.offset > this.remainder) {
        this.offset += this.remainder;
        this.totalBytes += 65536;
        return;
      } else {
        this.offset = 0;
        ({ value: this.chunk, done: this.done } = await this.reader.read());
        if (this.done && this.segmentOffset < downloads[this.id].files[this.path].realsize) {
          await this.getNextSegment();
          ({ value: this.chunk, done: this.done } = await this.reader.read());
        }
      }
    }

    if(this.bytes > 0) {
      this.totalBytes += this.bytes - 28;
    }

    return;
  }

  async padFile() {
    if (this.totalBytes % 512 > 0 && downloads[this.id].archive) {
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
      await this.output.write(downloads[this.id].files[this.path].header);
    } else {
      this.output.enqueue(downloads[this.id].files[this.path].header);
    }

    await this.getStart();

    while (!this.done) {
      if (cancelled) return;
      if (this.output instanceof WritableStream) {
        await this.output.write(this.chunk);
      } else {
        while(this.output.desiredSize <= 0) {
          await timeout(10);
        }
        this.output.enqueue(new Uint8Array(this.chunk));
      }
      this.totalBytes += this.chunk.length;
      ({ value: this.chunk, done: this.done } = await this.reader.read());

      if (this.done && this.segmentOffset < downloads[this.id].files[this.path].realsize) {
        await this.getNextSegment();
        ({ value: this.chunk, done: this.done } = await this.reader.read());
      }
    }

    // Round up to a multiple of 512, because tar
    await this.padFile();

    return;
  }

  async sliceFile() {
    // Get the first chunk from stream
    await this.getStart();

    // Slice the file and write decrypted content to output
    while (!this.done) {
      if (cancelled) return;
      await this.getSlice();

      if (this.output instanceof WritableStream) {
        // Write the decrypted contents directly in the file stream if
        // downloading to File System
        if (this.bytes > 0) {
          await this.output.write(decryptChunk(
            this.id,
            this.path,
            this.enChunkBuf.subarray(0, this.bytes),
          ));
        }
      } else {
        // Otherwise queue to the streamController since we're using a
        // ServiceWorker for downloading
        while(this.output.desiredSize <= 0) {
          await timeout(10);
        }
        if (this.bytes > 0) {
          this.output.enqueue(new Uint8Array(decryptChunk(
            this.id,
            this.path,
            this.enChunkBuf.subarray(0, this.bytes),
          )));
        }
      }
    }

    // Round up to a multiple of 512, because tar
    await this.padFile();

    // Free the session key
    Module.ccall(
      "free_crypt4gh_session_key",
      undefined,
      ["number"],
      [downloads[this.id].files[this.path].key],
    );
    return true;
  }

  async abortStream() {
    if (this.output instanceof WritableStream) {
      //stop writing to stream
      await this.output.abort();
    }
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

async function abortDownloads(direct, abortReason) {
  aborted = true;
  const msg = {
    eventType: "abort",
    reason: abortReason,
  };
  if (direct) {
    postMessage(msg);
  } else {
    self.clients.matchAll().then(clients => {
      clients.forEach(client =>
        client.postMessage(msg));
    });
  }
  clear();
  for (let id in downloads) {
    finishDownloadSession(id);
  }
}


// Safely free and remove a download session
function finishDownloadSession(id) {
  Module.ccall(
    "free_keypair",
    undefined,
    ["number"],
    [downloads[id].keypair],
  );
  delete downloads[id];
}


async function addSessionFiles(
  id,
  container,
  headers,
) {
  let undecryptable = false;

  for (const file in headers) {
    if (!createDownloadSessionFile(id, container, file, headers[file].header, headers[file].url, headers[file].size)) {
      undecryptable = true;
    }
  }

  return undecryptable;
}


async function beginDownloadInSession(
  id,
) {

  let fileHandle = downloads[id].handle;
  let fileStream;
  if (downloads[id].direct) {
    fileStream = await fileHandle.createWritable();
  } else {
    fileStream = fileHandle;
  }

  // Add the archive folder structure
  if (downloads[id].archive) {
    let folderPaths = Object.keys(downloads[id].files)
      .map(path => path.split("/"))  // split paths to items
      .map(path => path.slice(0, -1))  // remove the file names from paths
      .filter(path => path.length > 0)  // remove empty paths (root level files)
      .sort((a, b) => a.length - b.length)  // sort by path length as levels
      .reduce((unique, path) => {  // strip paths down to just the unique ones
        let check = unique.find(item => item === path.join("/"));
        if (check === undefined) {
          unique.push(path.join("/"));
        }
        return unique;
      }, []);

    for (const path of folderPaths) {
      if (downloads[id].direct) {
        await fileStream.write(
          addTarFolder(path),
        );
      } else {
        fileStream.enqueue(addTarFolder(path));
      }
    }
  }

  if (downloads[id].direct) {
    //get total download size and periodically report download progress
    for (const file in downloads[id].files) {
      totalToDo += downloads[id].files[file].size;
    }
    if (!downProgressInterval) {
      downProgressInterval = startProgressInterval();
    }
  }

  for (const file in downloads[id].files) {
    if (inServiceWorker) {
      self.clients.matchAll().then(clients => {
        clients.forEach(client =>
          client.postMessage({
            eventType: "downloadProgressing",
          }));
      });
    }

    let path = file.replace(".c4gh", "");

    if (downloads[id].archive) {
      const size = downloads[id].files[file].size;

      let fileHeader = addTarFile(
        downloads[id].files[file].key != 0 ? path : file,
        size,
      );

      if (downloads[id].direct) {
        await fileStream.write(fileHeader);
      } else {
        fileStream.enqueue(fileHeader);
      }
    }

    const slicer = new FileSlicer(
      fileStream,
      id,
      file);

    let res;
    if (downloads[id].files[file].key <= 0) {
      res = await slicer.concatFile().catch(() => {
        return false;
      });
    } else {
      res = await slicer.sliceFile().catch(() => {
        return false;
      });
    }
    if (!res) {
      await slicer.abortStream().then(async() => {
        //remove temporary files
        if (downloads[id].direct) {
          await downloads[id].handle.remove();
        }
      });
      if (!aborted) {
        await abortDownloads(!inServiceWorker, cancelled ? "cancel" : "error");
      }
      return;
    }
  }

  if (downloads[id].archive) {
    // Write the end of the archive
    if (downloads[id].direct) {
      await fileStream.write(enc.encode("\x00".repeat(1024)));
    } else {
      fileStream.enqueue(enc.encode("\x00".repeat(1024)));
    }
  }

  // Sync the file if downloading directly into file, otherwise finish
  // the fetch request.
  if (downloads[id].direct) {
    await fileStream.close();

  } else {
    fileStream.close();
  }

  if (downloads[id].direct) {
  // Direct downloads need no further action, the resulting archive is
  // already in the filesystem.
    postMessage({
      eventType: "finished",
      container: downloads[id].container,
    });
  } else {
  // Inform download with service worker finished
    self.clients.matchAll().then(clients => {
      clients.forEach(client =>
        client.postMessage({
          eventType: "finished",
          container: downloads[id].container,
        }));
    });
  }
  finishDownloadSession(id);
  return;
}

if (inServiceWorker) {
  // Add listener for fetch events
  self.addEventListener("fetch", (e) => {
    const url = new URL(e.request.url);

    let fileName;
    let containerName;
    let sessionId;

    if (fileUrl.test(url.pathname)) {
      fileName = url.pathname.replace(fileUrlStart, "");
      [sessionId, containerName] = url.pathname
        .replace("/file/", "").replace("/" + fileName, "").split("/");
    } else if (archiveUrl.test(url.pathname)) {
      fileName = url.pathname.replace(archiveUrlStart, "");
      [sessionId, containerName] = url.pathname
        .replace("/archive/", "")
        .replace(/\.tar$/, "")
        .split("/");
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
      downloads[sessionId].handle = streamController;

      // Start the decrypt slicer and respond, tell worker to stay open
      // until stream is consumed
      e.respondWith((() => {
        e.waitUntil(beginDownloadInSession(sessionId));
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
          createDownloadSession(e.data.id, e.data.container, undefined, false);
          e.source.postMessage({
            eventType: "getHeaders",
            id: e.data.id,
            container: e.data.container,
            files: [
              e.data.file,
            ],
            pubkey: downloads[e.data.id].pubkey,
            owner: e.data.owner,
            ownerName: e.data.ownerName,
          });
        }
      } else {
        createDownloadSession(
          e.data.id, e.data.container, e.data.handle, false);
        postMessage({
          eventType: "getHeaders",
          id: e.data.id,
          container: e.data.container,
          files: [
            e.data.file,
          ],
          pubkey: downloads[e.data.id].pubkey,
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
          createDownloadSession(e.data.id, e.data.container, undefined, true);
          e.source.postMessage({
            eventType: "getHeaders",
            id: e.data.id,
            container: e.data.container,
            files: e.data.files,
            pubkey: downloads[e.data.id].pubkey,
            owner: e.data.owner,
            ownerName: e.data.ownerName,
          });
        }
      } else {
        createDownloadSession(e.data.id, e.data.container, e.data.handle, true);
        postMessage({
          eventType: "getHeaders",
          id: e.data.id,
          container: e.data.container,
          files: e.data.files,
          pubkey: downloads[e.data.id].pubkey,
          owner: e.data.owner,
          ownerName: e.data.ownerName,
        });
      }
      break;
    case "addHeaders":
      if (aborted) return;
      addSessionFiles(e.data.id, e.data.container, e.data.headers).then(ret => {
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
          id: e.data.id,
          container: e.data.container,
          archive: downloads[e.data.id].archive,
          path: downloads[e.data.id].archive ? undefined
            : Object.keys(e.data.headers)[0],
        });
      } else {
        beginDownloadInSession(e.data.id);
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
    case "cancel":
      cancelled = true;
      break;
  }
});

waitAsm().then(() => {
  Module.ccall("libinit", undefined, undefined, undefined);
  libinitDone = true;
});

export var downloadRuntime = Module;
export var downloadFileSystem = FS;
