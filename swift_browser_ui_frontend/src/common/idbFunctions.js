// Functions for managing indexedDB
import {
  awsListBuckets,
  awsBulkAddBucketListCors,
} from "@/common/api";
import { getDB } from "@/common/idb";
import {
  DEV,
  tokenize,
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
  const existingContainers = await getDB()
    .containers.where({ projectID })
    .toArray();

  if (!signal) {
    const controller = new AbortController();
    signal = controller.signal;
  }

  let buckets;
  let continuationToken = undefined;
  let newBuckets = [];
  let newBucketsPage = [];

  do {
    buckets = [];

    // Get a list of buckets and check bucket CORS
    buckets = await awsListBuckets(projectID, continuationToken, 100);
    if (buckets?.Buckets?.length > 0) {
      await awsBulkAddBucketListCors(projectID, buckets.Buckets.map(
        bucket => bucket.Name,
      ));
    }

    if (buckets?.Buckets?.length > 0) {
      for (const bucket of buckets.Buckets) {

        let newBucket = {
          name: bucket.Name,
          tokens: tokenize(bucket.Name),
          projectID: projectID,
          tags: [],
          last_modified: bucket.CreationDate.toISOString(),
          bytes: 0,
          count: 0,
        };
        newBucketsPage.push(newBucket);

        if (newBucketsPage.length >= 100) {
          try {
            await getDB().containers.bulkPut(newBucketsPage);
          } catch (err) {
            if (DEV) console.log(err);
          }

          newBucketsPage = [];
        }

        newBuckets.push(newBucket);
      }
    }

    if (buckets?.ContinuationToken) {
      continuationToken = buckets.ContinuationToken;
    } else {
      break;
    }
    // May be unnecessary, S3 should omit the continuation token on
    // final page
    if (buckets?.Buckets?.length < 10) {
      break;
    }
  } while (buckets?.Buckets?.length > 0 && continuationToken);

  const sharedContainers = await getSharedContainers(projectID, signal);

  if (sharedContainers.length > 0) {
    for (let i in sharedContainers) {
      let cont = sharedContainers[i];
      cont.tokens =  cont.container.endsWith("_segments") ?
        [] : tokenize(cont.container);
      cont.projectID = projectID;
      cont.bytes = 0;
      cont.count = 0;
      cont.name = cont.container;

      const idb_last_modified = getContainerLastmodified(
        existingContainers, cont);
      cont.last_modified = !cont.container.endsWith("_segments") &&
        idb_last_modified  && idb_last_modified > cont.sharingdate ?
        idb_last_modified : cont.sharingdate;
    }

    await getDB()
      .containers.bulkPut(sharedContainers)
      .catch(() => {});
    newBuckets = newBuckets.concat(sharedContainers);
  }

  const toDelete = [];
  for (let i = 0; i < existingContainers.length; i++) {
    const oldCont = existingContainers[i];
    if (!newBuckets.find(cont => cont.name == oldCont.name)) {
      toDelete.push(oldCont.id);
    }
  }

  if (toDelete.length) {
    await getDB().containers.bulkDelete(toDelete);
  }
  const containersFromDB = await getDB()
    .containers.where({ projectID })
    .toArray();

  // sort "_segments" bucket before original bucket
  // so that "_segments" bucket could be updated first
  newBuckets = sortContainer(newBuckets);

  for (let i = 0; i < newBuckets.length; i++) {
    addSegmentContainerSize(newBuckets[i], newBuckets);
  }

  for (let i = 0; i < newBuckets.length; i++) {
    const container = newBuckets[i];
    const oldContainer = containersFromDB.find(
      cont => cont.name === container.name,
    );

    if (oldContainer !== undefined) {
      await getDB().containers.update(oldContainer.id, container);
    } else {
      await getDB().containers.put(container);
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
  await getDB().containers
    .where({ projectID: projectID, name: bucket})
    .modify(metadata);
}

export async function getBucketMetadata(projectID, bucket) {
  return await getDB().containers
    .get({ projectID: projectID, name: bucket});
}
