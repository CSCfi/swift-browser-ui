// Worker script for uploading objects using s3

// Upload information will be handled using Emscripten WorkerFS.
// WorkerFS allows us to use the files natively, which frees us from
// having to read the files fully in memory during transfer, and greatly
// simplifies operation.

// Worker gets a list of files to upload, general upload information,
// necessary file handles and slices. Worker will report finished chunks
// to the main thread for upload completion.

// Smaller files will be uploaded normally without using multipart uploads,
// the main thread is aware of the difference.

import { PutObjectCommand, S3Client, UploadPartCommand } from "@aws-sdk/client-s3";
import { checkPollutingName } from "./nameCheck";

let s3client = undefined;

waitAsm().then(() => {
  console.log("Assembler initialized, initalizing entropy source...");
  Module.ccall("libinit", undefined, undefined, undefined);
  console.log("Entropy source initalized.");
});

// Create an s3 client for the worker instance
function createS3Client(access, secret, endpoint) {
  if (s3client === undefined) {
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
}

async function encryptSegment (e) {
  console.log("Encrypting segment");
  let enChunk = Module.ccall(
    "encrypt_file_part",
    "number",
    ["array", "number", "string", "number"],
    [
      e.data.part.secret,
      e.data.part.size,
      `/${e.data.part.bucket}/${e.data.part.key}`,
      e.data.part.offset,
    ],
  );
  let enChunkPtr = Module.ccall(
    "wrap_chunk_content",
    "number",
    ["number"],
    [enChunk],
  );
  let enChunkLen = Module.ccall(
    "wrap_chunk_len",
    "number",
    ["number"],
    [enChunk],
  );

  // Create the AWS request and push the upload part
  console.log("Chunk encrypted, pushing chunk to multipart upload.");
  let command = undefined;
  let enBody = new Uint8Array(HEAPU8.subarray(enChunkPtr, enChunkPtr + enChunkLen));
  if (e.data.session !== "") {
    const input = {
      Body: enBody,
      Bucket: e.data.part.bucket,
      ContentLength: enChunkLen,
      Key: e.data.part.key.concat(".c4gh"),
      PartNumber: e.data.part.orderNumber,
      UploadId: e.data.session,
    };
    command = new UploadPartCommand(input);
  } else {
    const input = {
      Body: enBody,
      Bucket: e.data.part.bucket,
      ContentLength: enChunkLen,
      Key: e.data.part.key.concat(".c4gh"),
    }
    command = new PutObjectCommand(input);
  }

  console.log("Sending encrypted chunk via s3 client.")
  const completedPart = await s3client.send(command);

  postMessage({
    eventType: "progress",
    amount: e.data.part.size,
  });

  // Free the encrypted chunk content buffer
  console.log("Freeing encrypted chunk from buffer.");
  Module.ccall(
    "free_chunk",
    "number",
    ["number"],
    [enChunk],
  );

  postMessage({
    eventType: "uploadPartComplete",
    key: e.data.part.key,
    bucket: e.data.part.bucket,
    orderNumber: e.data.session !== "" ? e.data.part.orderNumber : 0,
    ETag: completedPart.ETag,
  });
}

self.addEventListener("message", (e) => {
  e.stopImmediatePropagation();

  // Sanity check container name
  if (checkPollutingName(e.data.bucket)) return;

  switch(e.data.command) {
    case "mountFiles":
      console.log(`Adding files to bucket ${e.data.bucket}`);
      FS.mkdir(`/${e.data.bucket}`);
      FS.mount(
        WORKERFS,
        {
          files: e.data.files.map(file => {
            console.log(`Mapping file with the name ${file.name}`);
            return file;
          }),
        },
        `/${e.data.bucket}`,
      );
      console.log("Successfully added the listed files.");
      postMessage({
        eventType: "filesAdded",
      });
      break;
    case "nextPart":
      encryptSegment(e).then(() => {});
      break;
    case "createS3Client":
      createS3Client(e.data.access, e.data.secret, e.data.endpoint);
      break;
    case "uploadFinished":
      FS.umount(`/${e.data.bucket}`);
      FS.rmdir(`/${e.data.bucket}`);
      postMessage({
        eventType: "filesRemoved",
      });
      break;
  }
});
