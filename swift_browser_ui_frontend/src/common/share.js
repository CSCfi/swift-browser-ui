// Functions for managing sharing
import store from "@/common/store";
import { DEV } from "./globalFunctions";
import { getDB } from "./idb";
import { getBucketPolicyStatements } from "./s3commands";

export async function getSharingContainers (projectId, signal) {
  // Get buckets a project has shared
  return store.state.client && projectId
    ? await store.state.client.getShare(projectId, signal)
    : [];
}

export async function getSharedContainers (projectId, signal) {
  // Get buckets shared to a project
  let ret = store.state.client
    ? await store.state.client.getAccess(projectId, signal)
    : [];

  return ret.filter(accessEntry => {
    return accessEntry.owner != projectId;
  });
}

export async function getAccessDetails (
  projectId,
  bucketName,
  sourceProjectId,
  signal)
{
  return store.state.client
    ? await store.state.client.getAccessDetails(
      projectId,
      bucketName,
      sourceProjectId,
      signal)
    : [];
}

export async function deleteStaleShares(project, bucket) {
  // Delete share entries of a deleted bucket in DB
  const client = store.state.client;

  async function deleteShareEntries(bucketName) {
    const shareDetails = await client.getShareDetails(project, bucketName);
    const shares = shareDetails.map(item => item.sharedTo);
    if (shares.length) await client.shareDeleteAccess(project, bucketName, shares);
  }

  await deleteShareEntries(bucket);
  // Delete corresponding _segments shares
  await deleteShareEntries(`${bucket}_segments`);
}

export async function syncBucketPolicies(project) {
  // Sync bucket policies to sharing DB according to s3 bucket policies
  const client = store.state.client;

  const buckets = await getDB()
    .containers
    .where({ projectID : project })
    .toArray();
  const bucketnames = buckets.map(b => b.name);

  // Refresh current sharing information
  let currentSharingDB = await client.getShare(project);
  // Prune any entries outside of current up-to-date bucket list
  for (let container of currentSharingDB) {
    if (!bucketnames.includes(container)) {
      const shareDetails = await client.getShareDetails(project, container);
      const shares = shareDetails.map(item => item.sharedTo);
      await client.shareDeleteAccess(project, container, shares);
    }
  }

  // Check bucket policies and sync sharing db
  for (let bucket of bucketnames) {
    // Get sharing information for bucket
    const shareDetails = await client.getShareDetails(project, bucket);
    let statements = [];
    try {
      statements = await getBucketPolicyStatements(bucket);
    } catch (e) {
      if (DEV) console.log(e.message);
    }
    // Build dict of current share recipients and their access rights (from db)
    let currentPolicies = {};
    for (let shareDetail of shareDetails) {
      const shareRecipient = shareDetail.sharedTo;
      const sharePolicy = {
        read: shareDetail.access.includes("r"),
        write: shareDetail.access.includes("w"),
      };
      currentPolicies[shareRecipient] = sharePolicy;
    }

    // Keep track of unused shares
    let toBeDeleted = Object.keys(currentPolicies);

    // compare current sharing db data with s3 bucketpolicy data, prune old data
    for (let statement of statements) {
      const principal = statement.Principal.AWS;
      if (principal === undefined) {
        continue;
      }
      const shareID = principal.match(/::([0-9a-fA-F]+):root$/)[1];
      const currentPolicy = currentPolicies[shareID];
      const bucketPolicy = {
        read: statement.Action.includes("s3:GetObject"),
        write: statement.Action.includes("s3:PutObject"),
      };

      toBeDeleted = toBeDeleted.filter(item => item !== shareID);

      if (
        bucketPolicy.read == currentPolicy?.read &&
        bucketPolicy.write == currentPolicy?.write
      ) {
        // Policies match, no action needed
        continue;
      }

      let accesslist = [];
      if (bucketPolicy.read) {
        accesslist.push("r");
      }
      if (bucketPolicy.write) {
        accesslist.push("w");
      }

      if (currentPolicies?.shareID) {
        // Existing shares need to be edited
        await client.shareEditAccess(
          project,
          bucket,
          [shareID],
          accesslist,
          "none",
        );
      } else {
        await client.shareNewAccess(
          project,
          bucket,
          [shareID],
          accesslist,
          "none",
        );
      }
    }
    // delete unusued shares
    if (toBeDeleted.length !== 0) {
      await client.shareDeleteAccess(project, bucket, toBeDeleted);
    }
  }
}
