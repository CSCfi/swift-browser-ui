// Tar convenience functions

function calcChecksum(header) {
  let checksum = 0;
  for(let i = 0, length = 512; i < length; i++) {
    checksum += header.charCodeAt(i);
  }
  let checksumStr = checksum.toString(8).padStart(6, "0") + "\x00 ";
  return checksumStr;
}

// Convert a header to an array, since TextEncoder can't deal with non 7-bit ASCII
function convertToArray(header) {
  let ret = [];

  for (let i = 0; i < header.length; i++) {
    ret.push(header.charCodeAt(i));
  }

  return new Uint8Array(ret);
}

const headerEnd =
  //header end (355B) same for all cases
  "\x00".repeat(100)  // Linked file name, 100 bytes, skip as NUL
  + "ustar "  // ustar indicator
  + " \x00"  // ustar version
  + "\x00".repeat(32)  // Owner user name
  + "\x00".repeat(32)  // Owner group name
  + "0000000\x000000000\x00" // device major and minor numbers
  + "\x00".repeat(12) // last accessed, atime
  + "\x00".repeat(12)// last changed, ctime
  // skip as NUL the following:
  // offset[12], longnames[4], unused[1],
  // sparse[4*24], isextended[1], realsize[12]
  + "\x00".repeat(126)
  + "\x00".repeat(17) // pad to 512 bytes
;

// Add a folder to the tar archive structure
export function addTarFolder(path) {
  let mtime = Math.floor(Date.now() / 1000).toString(8);
  let header = "";

  if (path.length > 100) {

    //extra header block for long path name
    let lBlock =
      "././@LongLink" + "\x00".repeat(87)
      + "0000755\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII, 11 bytes + padding NUL
      + (path.length + 1).toString(8).padStart(11, "0") + "\x00"
      // Last modification, not used, 11 bytes + padding NUL
      + "00000000000\x00"
      + "        "  // checksum placeholder
      + "L" // 1 byte type flag, L for long pathname
      + headerEnd
    ;
    //next block is the whole path
    let pathBlock = path;
    //pad the path to be divisable by 512 to get full blocks
    const pathRemainder = path.length % 512;

    if (pathRemainder !== 0) {
      let padding = 512 - pathRemainder;
      pathBlock += "\x00".repeat(padding);
    }

    lBlock = lBlock.replace("        ", calcChecksum(lBlock));

    let regularBlock =
      path.substring(0, 100)  // when path too long, truncate
      + "0000755\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII, 11 bytes + padding NUL
      + "00000000000\x00"
      // Last modification, not used, 11 bytes + padding NUL
      + mtime.padStart(11, "0") + "\x00"
      + "        "  // checksum placeholder
      + "5"  // 1 byte type flag, 5 for folder
      + headerEnd
    ;
    regularBlock = regularBlock.replace("        ", calcChecksum(regularBlock));
    // Calculate checksum in between to ease header calculation
    header = lBlock.concat(pathBlock, regularBlock);

  } else {

    header =
      path.padEnd(100, "\x00") // Tar name, max 100 char padded with NUL
      + "0000755\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      + "00000000000\x00"  // Size in octal ASCII, 11 bytes + padding NUL
      // Last modification, 11 bytes + padding nul
      + mtime.padStart(11, "0") + "\x00"
      + "        "  // checksum placeholder
      + "5"  // 1 byte type flag, 5 for folder
      + headerEnd
    ;
    header = header.replace("        ", calcChecksum(header));
  }
  return convertToArray(header);
}

// Add a file to the tar archive structure
export function addTarFile(path, size) {
  let mtime = Math.floor(Date.now() / 1000).toString(8);
  let header = "";
  let sizeStr = "";
  let maxOctal = 8589934592;

  if (size <= maxOctal) {
    //display smaller sizes than 8GiB in octal
    sizeStr = size.toString(8).padStart(11, "0") + "\x00";
  } else {
    //use base256 (signed) for larger numbers
    let bytes = BigInt(size);

    let base256 = [];
    do {
      base256.unshift(Number(bytes%256n));
      bytes = bytes/256n;
    } while (bytes);

    while (base256.length < 12) base256.unshift(0);
    base256[0] |= 0x80;
    base256 = base256.map(i => String.fromCharCode(i));
    sizeStr = base256.join("");
  }

  if (path.length > 100) {

    //extra header block for long path name
    let lBlock =
      "././@LongLink" + "\x00".repeat(87)
      + "0000644\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Path length in octal ASCII, 11 bytes + padding NUL
      + (path.length + 1).toString(8).padStart(11, "0") + "\x00"
      // Last modification, not used, 11 bytes + padding NUL
      + "00000000000\x00"
      + "        "  // checksum placeholder
      + "L" // 1 byte type flag, L for long pathname
      + headerEnd
    ;

    let pathBlock = path;
    //pad the path to be divisable by 512 to get full blocks
    const pathRemainder = path.length % 512;

    if (pathRemainder !== 0) {
      let padding = 512 - pathRemainder;
      pathBlock += "\x00".repeat(padding);
    }

    lBlock = lBlock.replace("        ", calcChecksum(lBlock));

    let regularBlock =
      path.substring(0, 100)  // when path too long, truncate to 100
      + "0000644\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII or base256, 11 bytes + padding NUL
      + sizeStr
      // Last modification, not used, 11 bytes + padding NUL
      + mtime.padStart(11, "0") + "\x00"
      + "        "  // checksum placeholder
      + "0"  // 1 byte type flag, 0 for normal file
      + headerEnd
    ;
    regularBlock = regularBlock.replace("        ", calcChecksum(regularBlock));
    // Calculate checksum in between to ease header calculation
    header = lBlock.concat(pathBlock, regularBlock);

  } else {
    header =
      path.padEnd(100, "\x00")  // Tar name, 100 char padded with NUL
      + "0000644\x00"  // File mode, 7 bytes octal + padding NUL
      // Owner UID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Owner GID, 7 bytes octal + padding NUL, default to root
      + "0000000\x00"
      // Size in octal ASCII or base256, 11 bytes + padding NUL
      + sizeStr
      // Last modification, not used, 11 bytes + padding NUL
      + mtime.padStart(11, "0") + "\x00"
      + "        "  // checksum placeholder
      + "0"  // 1 byte type flag, 0 for normal file
      + headerEnd
    ;

    // Calculate checksum in between to ease header calculation
    header = header.replace("        ", calcChecksum(header));
  }

  return convertToArray(header);
}
