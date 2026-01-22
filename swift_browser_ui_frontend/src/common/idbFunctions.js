// Functions for managing indexedDB
import {
  awsListBuckets,
} from "@/common/api";
import { getDB } from "@/common/idb";
import {
  DEV,
} from "@/common/globalFunctions";
import { getSharedContainers } from "@/common/share";

// Find the segments container matching a container (if it exists) and
// correctly update the container size using the size of the segments
// container.
function addSegmentContainerSize(container, containers) {
  let segments = containers.find(el => el.name === `${container.name}_segments`);
  if (segments !== undefined) {
    container.bytes += segments.bytes;
  }
}

function getContainerLastmodified(containers, cont) {
  // Get the current container and its last_modified from IDB
  const idb_cont = containers.find(
    el => el.name === cont.name && el.last_modified);
  const idb_last_modified = idb_cont ? idb_cont.last_modified : null;

  // Compare the last_modified from current container with
  // IDB container, choose the latest one
  if (idb_last_modified &&
    (idb_last_modified > cont.last_modified) ||
    (!cont.last_modified)
  ) {
    return idb_last_modified;
  }
  return cont.last_modified;
}

function sortContainer(containers) {
  // sort "_segments" bucket before original bucket
  return containers.sort((a, b) => {
    if (a.name === `${b.name}_segments`) {
      return -1;
    } else if (b.name === `${a.name}_segments`) {
      return 1;
    }
  });
}

export async function updateContainers(projectID, signal) {
  // STEP 1. Process project-owned buckets.

  // Get project buckets from IDB
  const idbBuckets = await getDB()
    .containers.where({ projectID })
    .toArray();

  // Create a bucket map for fast lookup
  const idbBucketsByName = new Map(idbBuckets.map((bucket) => [bucket.name, bucket]));
  // Track all existing buckets for IDB cleanup
  const existingBucketNames = new Set();

  if (!signal) {
    const controller = new AbortController();
    signal = controller.signal;
  }

  let buckets = [];
  let newBucketsPage = [];

  const maxBuckets = 100;

  // Get a list of buckets
  buckets = await awsListBuckets(projectID);

  if (buckets?.Buckets?.length > 0) {
    for (const bucket of buckets.Buckets) {
      // If bucket doesn't exist in IDB, add
      const bucketExists = idbBucketsByName.get(bucket.Name);

      if (!bucketExists) {
        // Bucket not in IDB, prepare new entry
        // bytes, count, last_modified are updated in objects view
        let newBucket = {
          name: bucket.Name,
          bytes: 0,
          count: 0,
          created: bucket.CreationDate.toISOString(),
          last_modified: bucket.CreationDate.toISOString(),
          projectID: projectID,
          cors_added: false, // added later
        };
        newBucketsPage.push(newBucket);
      }
      // Track all existing buckets
      existingBucketNames.add(bucket.Name);

      if (newBucketsPage.length >= maxBuckets) {
        await processBatch();
      }
    }
    // Process any remaining buckets after loop
    await processBatch();
  }

  async function processBatch() {
    if (newBucketsPage.length) {
      // Add buckets to IDB
      try {
        await getDB().containers.bulkPut(newBucketsPage);
        newBucketsPage = [];
      } catch (err) {
        if (DEV) console.log("Error adding buckets to IDB:", err);
      }
    }
  }

  // STEP 2. Process buckets your project has access to.
  const sharedBuckets = await getSharedContainers(projectID, signal);

  let newSharedBuckets = [];

  if (sharedBuckets.length) {
    for (const bucket of sharedBuckets) {

      const sharedBucketExists = idbBucketsByName.get(bucket.container);

      if (!sharedBucketExists) {
        const newSharedBucket = {
          name: bucket.container,
          bytes: 0,
          count: 0,
          last_modified: bucket.sharingdate,
          projectID: projectID,
          owner: bucket.owner,
        };
        newSharedBuckets.push(newSharedBucket);
      }
      existingBucketNames.add(bucket.container);
    }
    if (newSharedBuckets.length) {
      await getDB()
        .containers.bulkPut(newSharedBuckets)
        .catch(() => {});
      newSharedBuckets = [];
    }
  }

  // STEP 3. Delete non-existent buckets from IDB.
  const toDelete = [];

  for (const [name, bucket] of idbBucketsByName) {
    const bucketExists = existingBucketNames.has(name);
    if (!bucketExists) {
      // if bucket in IDB but not latest listing
      toDelete.push(bucket.id);
    }
  }

  if (toDelete.length) {
    try {
      await getDB().containers.bulkDelete(toDelete);
    } catch (err) {
      if (DEV) console.log(err);
    }
  }
}

export async function updateContainerLastmodified(
  projectID,
  container,
  objects,
) {
  // Declare the latest last_modified of container
  let cont_last_modified = container.last_modified;

  const last_modified_arr = objects.map(obj => obj.last_modified);

  // Find the latest last_modified among all objects,
  // compare it with the current last_modified of container,
  // assign the latest last_modified for container
  for (let i = 0; i < last_modified_arr.length; i++) {
    if (last_modified_arr[i] > cont_last_modified) {
      cont_last_modified = last_modified_arr[i];
    }
  }

  // Assign the latest last_modified of objects to parent container
  if (cont_last_modified) {
    await getDB().containers
      .where({ projectID: projectID, name: container.name})
      .modify({ last_modified: cont_last_modified });
  }
}

export async function saveBucketMetadata(projectID, bucket, metadata) {
  // Modify only select fields that receive data from objects
  const updatedMetadata = {
    bytes: metadata.bytes,
    count: metadata.count,
    last_modified: metadata.last_modified,
  };
  await getDB().containers
    .where({ projectID: projectID, name: bucket})
    .modify(updatedMetadata);
}

export async function getBucketMetadata(projectID, bucket) {
  return await getDB().containers
    .get({ projectID: projectID, name: bucket});
}

export async function checkCorsFlag(projectID, bucket) {
  const idbBucket = await getDB().containers
    .get({ projectID: projectID, name: bucket});
  return idbBucket?.cors_added; // undefined on shared buckets
}

export async function updateCorsFlag(projectID, buckets, corsAdded) {
  try {
    await getDB().containers
      .where("[projectID+name]")
      .anyOf(buckets.map(name => [projectID, name]))
      .modify(bucket => bucket.cors_added = corsAdded);
  } catch {
    if (DEV) console.log("Error updating IDB bucket CORS flag");
  }
}
