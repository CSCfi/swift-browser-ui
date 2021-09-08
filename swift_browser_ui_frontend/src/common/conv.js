import {
  getBucketMeta,
  getAccessControlMeta,
} from "./api";

export default function getLangCookie() {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + "OBJ_UI_LANG" + "=([^;]*)",
  ));
  return matches ? decodeURIComponent(matches[1]) : "en";
}

function shiftSizeDivision(vallist) {
  "use strict";
  // Javascript won't let us do anything but floating point division by
  // default, so a different approach was chosen anyway.
  //  ( right shift by ten is a faster alias to division by 1024,
  //  decimal file sizes are heresy and thus can't be enabled )
  switch (vallist[0] >>> 10) {
    case 0:
      return vallist;
    default:
      vallist[0] = vallist[0] >>> 10;
      vallist[1] = vallist[1] + 1;
      return shiftSizeDivision(vallist);
  }
}

function check_duplicate(container, share, currentdetails) {
  for (let detail of currentdetails) {
    if (detail.container == container && detail.sharedTo == share) {
      return true;
    }
  } return false;
}

export async function syncContainerACLs(client, project) {
  let acl = await getAccessControlMeta();

  let amount = 0;
  let aclmeta = acl.access;
  let currentsharing = await client.getShare(project);

  // Delete stale shared access entries from the database
  console.log(currentsharing);
  for (let container of currentsharing) {
    console.log("checking container existence for ", container);
    console.log(aclmeta);
    console.log("compare: ", !(Object.keys(aclmeta).includes(container)));
    if (!(Object.keys(aclmeta).includes(container))) {
      console.log("container", container, " no longer exists, removing");
      let resp = await client.shareContainerDeleteAccess(
        project,
        container,
      );
      if (resp) {
        console.log("container access deletion successful");
      } else {
        console.log("container access deletion failed");
      }
    } else {
      continue;
    }
  }

  // sync new shares into the sharing database
  for (let container of Object.keys(aclmeta)) {
    console.log("adding new containers per ACL listing");
    let currentdetails = [];
    if (currentsharing.includes(container)) {
      currentdetails = await client.getShareDetails(
        project,
        container,
      );
    }
    for (let share of Object.keys(aclmeta[container])) {
      if (check_duplicate(container, share, currentdetails)) {
        continue;
      }
      let accesslist = [];
      if (aclmeta[container][share].read) {
        accesslist.push("r");
      }
      if (aclmeta[container][share].write) {
        accesslist.push("w");
      }
      await client.shareNewAccess(
        project,
        container,
        [share],
        accesslist,
        acl.address,
      );
      amount++;
    }
  }
  return amount;
}

export function getHumanReadableSize(val) {
  // Get a human readable version of the size, which is returned from the
  // API as bytes, flooring to the most significant size without decimals.

  // As JS doesn't allow us to natively handle 64 bit integers, ditch all
  // unnecessary stuff from the value, we only need the significant part.
  let byteval = val > 4294967296 ? parseInt(val / 1073741824) : val;
  let count = val > 4294967296 ? 3 : 0;

  let human = shiftSizeDivision([byteval, count]);
  let ret = human[0].toString();
  switch (human[1]) {
    case 0:
      ret += " B";
      break;
    case 1:
      ret += " KiB";
      break;
    case 2:
      ret += " MiB";
      break;
    case 3:
      ret += " GiB";
      break;
    case 4:
      ret += " TiB";
      break;
  }
  return ret;
}

export async function getTagsForContainer(containerName) {
  let tags = [];
  await getBucketMeta(containerName).then(meta => {
    if ("usertags" in meta[1]) {
      tags = meta[1]["usertags"].split(";");
    }
  });
  return tags;
}
