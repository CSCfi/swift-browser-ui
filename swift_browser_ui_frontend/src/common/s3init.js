import {
  S3Client,
} from "@aws-sdk/client-s3";
import { GET } from "./api";
import { DEV } from "./conv";
import S3UploadSocket from "./s3upload";
import S3DownloadSocket from "./s3download";

let initPromise = null;

// Fetch S3 endpoint from backend
async function discoverEndpoint() {
  let endpointUrl = new URL("/discover/s3", document.location.origin);
  let resp = await GET(endpointUrl);
  resp = await resp.json();
  return resp.s3api_endpoint;
}

// Get the EC2 credentials from backend, for S3 operations in frontend.
export async function getEC2Credentials(projectID) {
  let fetchURL = new URL(`/api/${encodeURI(projectID)}/OS-EC2`, document.location.origin);
  let resp = await GET(fetchURL);

  if (resp.status != 200) {
    throw new Error("Failed to retrieve EC2 credentials.");
  }

  return await resp.json();
}

// Create a client for accessing the S3 API
function createClient(accessKey, secretKey, endpoint) {
  return new S3Client({
    region: "us-east-1",
    endpoint: endpoint,
    credentials: {
      accessKeyId: accessKey,
      secretAccessKey: secretKey,
    },
  });
}

export async function initS3(projectID, projectName, store, t) {
  if (initPromise) return initPromise;
  initPromise = (async () => {
    if (DEV) console.log("Initializing S3 client...");
    const s3endpoint = await discoverEndpoint();
    store.commit("setS3Endpoint", s3endpoint);

    const ec2creds = await getEC2Credentials(projectID);

    // Initialize the frontend S3 client
    const s3client = createClient(
      ec2creds.access,
      ec2creds.secret,
      s3endpoint,
    );
    store.commit("setS3Client", s3client);

    // Initialize the S3 upload implementation
    const s3upsocket = new S3UploadSocket(
      projectID,
      projectName,
      store,
      t,
      s3client,
      ec2creds.access,
      ec2creds.secret,
      s3endpoint,
    );
    store.commit("setS3Upload", s3upsocket);

    // Initialize the S3 download implementation
    const s3downsocket = new S3DownloadSocket(
      projectID,
      projectName,
      store,
      t,
      s3client,
      ec2creds.access,
      ec2creds.secret,
      s3endpoint,
    );
    store.commit("setS3Download", s3downsocket);
  })()
    .then(() => {
      if (DEV) console.log("S3 client initialized");
    })
    .catch((error) => {
      initPromise = null;
      throw error;
    });
  return initPromise;
}