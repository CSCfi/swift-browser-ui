// Swift cross account container sharing API JavaScript bindings module.

import {
  GET,
} from "@/common/api";

class SwiftXAccountSharing {
  // Swift cross account sharing backend client.

  constructor(
    address,
    signatureAddress = "",
  ) {
    this.address = address;
    this.signatureAddress = signatureAddress;
  }

  _parseListString(
    toParse,
  ) {
    // Parse the JS list into comma separated values in string.
    let ret = "";
    toParse.forEach(user => {
      ret = ret.concat(user, ",");
    });
    return ret.slice(0, ret.length - 1);
  }

  async _getSignature(
    validFor,
    toSign,
  ) {
    // Get a signature for an API call.
    if (this.signatureAddress != "") {
      let signatureUrl = new URL("/sign/".concat(validFor),
        this.signatureAddress);
      signatureUrl.searchParams.append("path", toSign);
      let signed = await GET(signatureUrl);
      return signed.json();
    }
    else {
      return undefined;
    }
  }

  async getAccess(
    username,
    signal,
  ) {
    // List the containers the user has been given access to.
    let url = new URL(this.address.concat("/access/", username));

    let signed = await this._getSignature(
      60,
      "/access/".concat(username),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let containers = fetch(
      url, { method: "GET", signal },
    ).then(
      (resp) => { return resp.json(); },
    ).catch((err) => {
      if (signal.aborted) return [];
      throw new Error(err);
    });
    return containers;
  }

  async getAccessDetails(
    username,
    container,
    owner,
    signal,
  ) {
    // Get details from a container the user has been given access to.
    let url = new URL(
      this.address.concat("/access/", username, "/", container),
    );

    let signed = await this._getSignature(
      60,
      "/access/".concat(username, "/", container),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    url.searchParams.append("owner", owner);
    let details = fetch(
      url, { method: "GET", signal },
    ).then(
      (resp) => { return resp.json(); },
    ).catch((err) => {
      if (signal.aborted) return [];
      throw new Error(err);
    });
    return details;
  }

  async getShare(
    username,
    signal,
  ) {
    // List the containers the user has shared to another user / users.
    let url = new URL(this.address.concat("/share/", username));

    let signed = await this._getSignature(
      60,
      "/share/".concat(username),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let shared = fetch(
      url, { method: "GET", signal },
    ).then(
      (resp) => { return resp.json(); },
    ).catch((err) => {
      if (signal.aborted) return [];
      throw new Error(err);
    });
    return shared;
  }

  async getShareDetails(
    username,
    container,
    signal,
  ) {
    // Get details from a container the user has given access to.
    let url = new URL(
      this.address.concat("/share/", username, "/", container),
    );

    let signed = await this._getSignature(
      60,
      "/share/".concat(username, "/", container),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let details = fetch(
      url, { method: "GET", signal },
    ).then(
      (resp) => { return resp.json(); },
    ).catch((err) => {
      if (signal?.aborted) return [];
      throw new Error(err);
    });
    return details;
  }

  async shareNewAccess(
    username,
    container,
    userlist,
    accesslist,
    address,
  ) {
    // Upload details about a new share action.
    let url = new URL(
      this.address.concat("/share/", username, "/", container),
    );
    url.searchParams.append("user", this._parseListString(userlist));
    url.searchParams.append("access", this._parseListString(accesslist));
    url.searchParams.append("address", address);

    let signed = await this._getSignature(
      60,
      "/share/".concat(username, "/", container),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let shared = fetch(
      url, { method: "POST" },
    ).then(
      (resp) => {
        if (resp.status == 409) {
          throw new Error("Container already shared.");
        }
        return resp.json();
      },
    );
    return shared;
  }

  async shareEditAccess(
    username,
    container,
    userlist,
    accesslist,
  ) {
    // Edit the details of an existing share action.
    let url = new URL(
      this.address.concat("/share/", username, "/", container),
    );
    url.searchParams.append("user", this._parseListString(userlist));
    url.searchParams.append("access", this._parseListString(accesslist));

    let signed = await this._getSignature(
      60,
      "/share/".concat(username, "/", container),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let shared = fetch(
      url, { method: "PATCH" },
    ).then(
      (resp) => { return resp.json(); },
    );
    return shared;
  }

  async shareDeleteAccess(
    username,
    container,
    userlist,
  ) {
    // Delete the details of an existing share action.
    let url = new URL(
      this.address.concat("/share/", username, "/", container),
    );

    let signed = await this._getSignature(
      60,
      "/share/".concat(username, "/", container),
    );

    url.searchParams.append("user", this._parseListString(userlist));
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let deleted = fetch(
      url, { method: "DELETE" },
    ).then(
      (resp) => {
        return resp.status == 204 ? true : false;
      },
    );
    return deleted;
  }

  async shareContainerDeleteAccess(
    username,
    container,
  ) {
    // Delete all shares on a container
    let url = new URL(
      this.address.concat("/share/", username, "/", container),
    );

    let signed = await this._getSignature(
      60,
      "/share/".concat(username, "/", container),
    );

    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let deleted = fetch(
      url, { method: "DELETE" },
    ).then(
      (resp) => {
        return resp.status == 204 ? true : false;
      },
    );
    return deleted;
  }

  async projectCacheIDs(
    id,
    name,
  ) {
    // Cache the identifier information of a project
    let url = new URL(
      this.address.concat("/ids/", id),
    );

    let signed = await this._getSignature(
      60,
      "/ids/".concat(id),
    );

    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let added = fetch(
      url, {
        method: "PUT",
        body: name,
      },
    ).then(
      (resp) => {
        return resp.status == 204 ? true : false;
      },
    );

    return added;
  }

  async projectCheckIDs(
    id,
  ) {
    // Check a cached ID
    let url = new URL(
      this.address.concat("/ids/", id),
    );

    let signed = await this._getSignature(
      60,
      "/ids/".concat(id),
    );

    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let check = fetch(
      url, {
        method: "GET",
      },
    ).then(
      (resp) => {
        if (resp.status == 200) {
          return resp.json();
        }
        else return undefined;
      },
    );

    return check;
  }
}

export default SwiftXAccountSharing;
