// Worker scripts for download chunks

import { addTarFile, addTarFolder } from "./tar";
import { checkPollutingName } from "./nameCheck";
import { GetObjectCommand, HeadObjectOutputFilterSensitiveLog, S3Client, WriteGetObjectResponseCommand } from "@aws-sdk/client-s3";

/*
Schema for storing the download information:
{
  "bucketName": {  // Bucket level session for the download
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

// Use a 50 MiB segment when downloading
const DOWNLOAD_ENCRYPTED_SEGMENT_SIZE = 52451200; // 50 MiB after decryption
const DOWNLOAD_UNENCRYPTED_SEGMENT_SIZE = 52428800; // 50 MiB

let s3client = undefined;

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

function createS3Client(access, secret, endpoint) {
  s3client = new S3Client({
    region: "RegionOne",
    stsRegionalEndpoints: "legacy",
    s3UsEast1RegionalEndpoint: "legacy",
    s3ForcePathStyle: true,
    forcePathStyle: true,
    endpoint: endpoint,
    credentials: {
      accessKeyId: access,
      secretAccessKey: secret,
    },
  });

  postMessage({
    eventType: "s3ClientCreated",
  });
}

if (inServiceWorker) {
  self.addEventListener("install", (event) => {
    event.waitUntil(waitAsm());
  });
  self.addEventListener("activate", (event) => {
    event.waitUntil(self.clients.claim());
  });
}

// Create a download session
function createDownloadSession(id, bucket, handle, archive, test = false) {
  aborted = false; // reset

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
    bucket: bucket,
    test: test,
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
function createDownloadSessionFile(id, bucket, path, header, url, size) {
  if (checkPollutingName(path)) return;

  let headerPath = `header_${bucket}_`
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

async function sliceChunk(output, id, path, body, offset, size=65564) {
  let chunk, chunkPtr, chunkLen;

  chunk = Module.ccall(
    "decrypt_chunk",
    "number",
    ["number", "array", "number"],
    [
      downloads[id].files[path].key,
      body.slice(offset, offset + size),
      size,
    ],
  );
  chunkPtr = Module.ccall(
    "wrap_chunk_content",
    "number",
    ["number"],
    [chunk],
  );
  chunkLen = Module.ccall(
    "wrap_chunk_len",
    "number",
    ["number"],
    [chunk],
  );
  // Don't clone the view, these writes can't happen in parallel.
  // ServiceWorker download will clone as necessary.
  if (output instanceof WritableStream) {
    await output.write(HEAPU8.subarray(chunkPtr, chunkPtr + chunkLen));
  } else {
    while(output.desiredSize <= 0) {
      await timeout(5);
    }
    output.enqueue(new Uint8Array(HEAPU8.subarray(chunkPtr, chunkPtr + chunkLen)));
  }
  totalDone += chunkLen;

  return chunkLen;
}

// Slice a file out from storage in approx 50 MiB segments.
async function sliceFile(output, id, path) {
  let totalSegments = Math.floor(downloads[id].files[path].realsize / DOWNLOAD_ENCRYPTED_SEGMENT_SIZE);
  let lastSegment = downloads[id].files[path].realsize % DOWNLOAD_ENCRYPTED_SEGMENT_SIZE;

  let totalBytes = 0;

  // Slice all segments of the file to output as decrypted
  for (let i = 0; i < totalSegments; i++) {
    const input = {
      Bucket: id,
      Key: path,
      Range: `bytes=${i * DOWNLOAD_ENCRYPTED_SEGMENT_SIZE}-${i * DOWNLOAD_ENCRYPTED_SEGMENT_SIZE + DOWNLOAD_ENCRYPTED_SEGMENT_SIZE}`,
    };
    const command = GetObjectCommand(input);
    const resp = await s3client.send(command);
    const body = await resp.Body.transformToByteArray();

    for (let j = 0; j < DOWNLOAD_ENCRYPTED_SEGMENT_SIZE; j += 65564) {
      totalBytes += await sliceChunk(output, id, path, body, j);
    }
  }

  // Slice the remainder segment if it exists
  if (lastSegment > 0) {
    const input = {
      Bucket: id,
      Key: path,
      Range: `bytes=${totalSegments * DOWNLOAD_ENCRYPTED_SEGMENT_SIZE}-${downloads[id].files[path].realsize}`
    };
    const command = GetObjectCommand(input);
    const resp = await s3client.send(command);
    const body = await resp.Body.transformToByteArray();

    for(let i = 0; i < lastSegment; i += 65564) {
      totalBytes += await sliceChunk(output, id, path, body, i);
    }

    // Slice the remainder if it exists
    if (lastSegment % 65564 > 0) {
      totalBytes += await sliceChunk(
        output,
        id,
        path,
        body,
        lastSegment - lastSegment % 65564,
        lastSegment % 65564
      );
    }
  }

  // Pad file to a multiple of 512 bytes if creating a tarball
  if (totalBytes % 512 < 0 && downloads[id].archive) {
    let padding = "\x00".repeat(512 - totalBytes % 512);
    if (output instanceof WritableStream) {
      await output.write(enc.encode(padding));
    } else {
      output.enqueue(enc.encode(padding));
    }
  }
}

async function concatFile(output, id, path) {
  let totalSegments = Math.floor(downloads[id].files[path].realsize / DOWNLOAD_UNENCRYPTED_SEGMENT_SIZE);
  let lastSegment = downloads[id].files[path].realsize % DOWNLOAD_UNENCRYPTED_SEGMENT_SIZE;
  let totalBytes = 0;

  // Slice through the file as unencrypted content
  for (let i = 0; i < totalSegments; i++) {
    const input = {
      Bucket: id,
      Key: path,
      Range: `bytes=${i * DOWNLOAD_UNENCRYPTED_SEGMENT_SIZE}-${i * DOWNLOAD_UNENCRYPTED_SEGMENT_SIZE + DOWNLOAD_UNENCRYPTED_SEGMENT_SIZE}`,
    };
    const command = GetObjectCommand(input);
    const resp = await s3client.send(command);
    const body = await resp.Body.transformToByteArray();

    if (output instanceof WritableStream) {
      await output.write(body);
    } else {
      while (output.desiredSize <= 0) {
        await timeout(5);
      }
      output.enqueue(body);
    }

    totalDone += DOWNLOAD_UNENCRYPTED_SEGMENT_SIZE;
    totalBytes += DOWNLOAD_ENCRYPTED_SEGMENT_SIZE;
  }

  if (lastSegment > 0) {
    const input = {
      Bucket: id,
      Key: path,
      Range: `bytes=${totalSegments * DOWNLOAD_UNENCRYPTED_SEGMENT_SIZE}-${downloads[id].files[path].realsize}`,
    };
    const command = GetObjectCommand(input);
    const resp = await s3client.send(command);
    const body = await resp.Body.transformToByteArray();

    if (output instanceof WritableStream) {
      await output.write(body);
    } else {
      while (output.desiredSize <= 0) {
        await timeout(5);
      }
      output.enqueue(body);
    }
  }
  totalDone += lastSegment;
  totalBytes += lastSegment;

  // Pad file to a multiple of 512 bytes if creating a tarball
  if (totalBytes % 512 < 0 && downloads[id].archive) {
    let padding = "\x00".repeat(512 - totalBytes % 512);
    if (output instanceof WritableStream) {
      await output.write(enc.encode(padding));
    } else {
      output.enqueue(enc.encode(padding));
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

function startAbort(direct, abortReason) {
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

async function abortDownload(id, stream = null) {
  if (downloads[id].direct) {
    //remove temp files
    if (stream) await stream.abort();
    await downloads[id].handle.remove();
  }
  finishDownloadSession(id);
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
    if (aborted) {
      await abortDownload(id, fileStream);
      return;
    }
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

    if (downloads[id].files[file].key <= 0) {
      res = await concatFile(fileStream, id, file).catch(() => {
        return false;
      });
    } else {
      res = await sliceFile(fileStream, id, file).catch(() => {
        return false;
      });
    }

    if (!res) {
      if (!aborted) startAbort(!inServiceWorker, "error");
      await abortDownload(id, fileStream);
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
      test: downloads[id].test,
      handle: downloads[id].handle,
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
    let bucketName;
    let sessionId;

    if (fileUrl.test(url.pathname)) {
      fileName = url.pathname.replace(fileUrlStart, "");
      [sessionId, bucketName] = url.pathname
        .replace("/file/", "").replace("/" + fileName, "").split("/");
    } else if (archiveUrl.test(url.pathname)) {
      fileName = url.pathname.replace(archiveUrlStart, "");
      [sessionId, bucketName] = url.pathname
        .replace("/archive/", "")
        .replace(/\.tar$/, "")
        .split("/");
    } else {
      return;
    }

    // Fix URL safe contents
    fileName = decodeURIComponent(fileName);
    bucketName = decodeURIComponent(bucketName);

    if (checkPollutingName(bucketName)) return;

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
        "attachment; filename=\"" +
          fileName.split("/").at(-1).replace(".c4gh", "") + "\"",
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
  // Sanity check bucket name
  if (checkPollutingName(e.data.bucket)) return;

  switch(e.data.command) {
    case "initS3Client":
      createS3Client(e.data.access, e.data.secret, e.data.endpoint);
      break;
    case "downloadFile":
      if (inServiceWorker) {
        while (!libinitDone) {
          await timeout(250);
        }
        if (libinitDone) {
          createDownloadSession(e.data.id, e.data.bucket, undefined, false);
          e.source.postMessage({
            eventType: "getHeaders",
            id: e.data.id,
            bucket: e.data.bucket,
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
          e.data.id, e.data.bucket, e.data.handle, false, e.data.test);
        postMessage({
          eventType: "getHeaders",
          id: e.data.id,
          bucket: e.data.bucket,
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
          createDownloadSession(e.data.id, e.data.bucket, undefined, true);
          e.source.postMessage({
            eventType: "getHeaders",
            id: e.data.id,
            bucket: e.data.bucket,
            files: e.data.files,
            pubkey: downloads[e.data.id].pubkey,
            owner: e.data.owner,
            ownerName: e.data.ownerName,
          });
        }
      } else {
        createDownloadSession(
          e.data.id, e.data.bucket, e.data.handle, true, e.data.test);
        postMessage({
          eventType: "getHeaders",
          id: e.data.id,
          bucket: e.data.bucket,
          files: e.data.files,
          pubkey: downloads[e.data.id].pubkey,
          owner: e.data.owner,
          ownerName: e.data.ownerName,
        });
      }
      break;
    case "addHeaders":
      addSessionFiles(e.data.id, e.data.bucket, e.data.headers).then(ret => {
        if (ret && inServiceWorker) {
          e.source.postMessage({
            eventType: "notDecryptable",
            bucket: e.data.bucket,
          });
        } else if (ret) {
          postMessage({
            eventType: "notDecryptable",
            bucket: e.data.bucket,
          });
        }
      }).catch(async () => {
        if (!aborted) startAbort(!inServiceWorker, "error");
        await abortDownload(e.data.id);
      });
      if (inServiceWorker) {
        e.source.postMessage({
          eventType: "downloadStarted",
          id: e.data.id,
          bucket: e.data.bucket,
          archive: downloads[e.data.id].archive,
          path: downloads[e.data.id].archive ? undefined
            : Object.keys(e.data.headers)[0],
        });
      } else {
        beginDownloadInSession(e.data.id);
        postMessage({
          eventType: "downloadStarted",
          bucket: e.data.bucket,
        });
      }
      break;
    case "keepDownloadProgressing":
      break;
    case "clear":
      clear();
      break;
    case "abort":
      if (!aborted) startAbort(!inServiceWorker, e.data.reason);
      break;
  }
});

waitAsm().then(() => {
  Module.ccall("libinit", undefined, undefined, undefined);
  libinitDone = true;
});

export var downloadRuntime = Module;
export var downloadFileSystem = FS;
