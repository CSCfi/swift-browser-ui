// Functions for managing sharing
import useStore from "@/common/store";
import { DEV } from "./globalFunctions";
import { getDB } from "./idb";
import { getBucketPolicyStatements } from "./s3commands";
import { updateCorsFlag } from "./idbFunctions";
import { awsBulkAddBucketListCors, signedFetch } from "./api";

function getSharingClient() {
  const store = useStore();
  return store.sharingClient;
}

export async function getSharingContainers (projectId, signal) {
  const sharingClient = getSharingClient();
  // Get buckets a project has shared
  return sharingClient && projectId
    ? await sharingClient.getShare(projectId, signal)
    : [];
}

export async function getSharedContainers (projectId, signal) {
  const sharingClient = getSharingClient();
  // Get buckets shared to a project
  let ret = sharingClient
    ? await sharingClient.getAccess(projectId, signal)
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
  const sharingClient = getSharingClient();
  return sharingClient
    ? await sharingClient.getAccessDetails(
      projectId,
      bucketName,
      sourceProjectId,
      signal)
    : [];
}

export async function deleteStaleShares(project, bucket) {
  // Delete share entries of a deleted bucket in DB
  const client = getSharingClient();

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
  if (DEV) console.log("Starting sharing sync...");
  const store = useStore();
  const projectName = store.active.name;

  const client = getSharingClient();
  // Add CORS and sync bucket policies to sharing DB according to s3 bucket policies

  const buckets = await getDB()
    .containers
    .where({ projectID : project })
    .toArray();

  const bucketsByName = new Map(buckets.map((bucket) => [bucket.name, bucket]));

  // Check CORS flag and add CORS in batches
  let toAddCors = [];
  const batchSize = 20;

  async function processBatch(buckets) {
    if (toAddCors.length) {
      try {
        await awsBulkAddBucketListCors(project, buckets);
        await updateCorsFlag(project, buckets, true);
      } catch (err) {
        if (DEV) console.log("Error adding CORS", err);
      }
    }
  }

  for (let [bucketName, bucket] of bucketsByName) {
    if (bucket?.cors_added === false) {
      toAddCors.push(bucketName);
    }
    if (toAddCors.length >= batchSize) {
      await processBatch(toAddCors);
      toAddCors = [];
    }
  }
  await processBatch(toAddCors);

  // Refresh current sharing information
  let currentSharingDB = [];
  try {
    currentSharingDB = await client.getShare(project);
  } catch(e) {
    console.error(`Failed to get share details for ${project}:`, e);
  }
  // Prune any entries outside of current up-to-date bucket list
  for (let container of currentSharingDB) {
    if (!bucketsByName.get(container)) {
      try {
        const shareDetails = await client.getShareDetails(project, container);
        const shares = shareDetails.map(item => item.sharedTo);
        await client.shareDeleteAccess(project, container, shares);
      } catch(e) {
        console.error(`Failed to prune share entries for ${container}:`, e);
      }
    }
  }

  // Check bucket policies and sync sharing db
  for (let [bucket] of bucketsByName) {
    // Get sharing information for bucket
    let shareDetails = [];
    try {
      shareDetails = await client.getShareDetails(project, bucket);
    } catch(e) {
      console.error(`Failed to retrieve share details for ${bucket}:`, e);
      continue;
    }
    let statements = [];
    try {
      statements = (await getBucketPolicyStatements(bucket))
        .filter(statement => statement?.Sid === "GrantSDConnectSharedAccessToProject");
    } catch (e) {
      // Don't delete shares if statements cannot be retrieved
      console.error(`Failed to fetch bucket policy for ${bucket}:`, e);
      continue;
    }
    // Build dict of current share recipients and their access rights (from db)
    let currentPolicies = {};
    for (let shareDetail of shareDetails) {
      const shareRecipient = shareDetail.sharedTo;
      const sharePolicy = shareDetail?.access;
      // View not listed, add for comparison
      if (sharePolicy) {
        sharePolicy.unshift("v");
      }
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

      // Check vault whitelist to distinguish between view and read
      const accesslist = [];
      try {
        const receiver = await client.projectCheckIDs(shareID);
        let resp = await signedFetch(
          "GET",
          store.uploadEndpoint,
          `/check/${projectName}/${bucket}/${receiver.name}`,
        );
        const whitelisted = resp.status === 204 ? false :
          resp.status === 200 ? true : null;

        if (bucketPolicy.read && !bucketPolicy.write && whitelisted === false) {
          accesslist.push("v");
        } else if (bucketPolicy.read && !bucketPolicy.write && whitelisted) {
          accesslist.push("v", "r");
        } else if (bucketPolicy.read && bucketPolicy.write && whitelisted) {
          accesslist.push("v", "r", "w");
        } else {
          throw new Error(`Incongruous bucket policy and sharing whitelist on ${bucket}`);
        }
      } catch(e) {
        console.error("Could not create a valid access list:", e);
        continue;
      }

      if (currentPolicy) {
        // Compare and update if needed
        const policiesMatch = accesslist.length === currentPolicy.length &&
          accesslist.every((p) => currentPolicy.includes(p));
        if (policiesMatch) {
          // Sharing DB matches bucket policies and vault
          continue;
        } else {
          try {
            await client.shareEditAccess(
              project,
              bucket,
              [shareID],
              accesslist,
              "none",
            );
            if (DEV) console.log("Updated a sharing entry for", bucket);
          } catch(e) {
            console.error(`Failed to update a sharing entry for ${bucket}:`, e);
          }
        }
      } else {
        try {
          await client.shareNewAccess(
            project,
            bucket,
            [shareID],
            accesslist,
            "none",
          );
          if (DEV) console.log("Added a new sharing entry for", bucket);
        } catch(e) {
          console.error(`Failed to update a sharing entry for ${bucket}:`, e);
        }
      }
    }
    // delete unused shares
    if (toBeDeleted.length !== 0) {
      try {
        await client.shareDeleteAccess(project, bucket, toBeDeleted);
      } catch(e) {
        console.error(`Failed to delete stale share entries for ${bucket}:`, e);
      }
    }
  }
  if (DEV) console.log("Sharing sync done.");
}
