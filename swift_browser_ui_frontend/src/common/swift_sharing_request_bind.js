// Swift cross account container sharing API JavaScript bindings module.

class SwiftSharingRequest {
  // Swift sharing request backend client.

  constructor(
    address,
    signatureAddress = "",
  ) {
    this.address = address;
    this.signatureAddress = signatureAddress;
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
      let signed = await fetch(
        signatureUrl, { method: "GET", credentials: "same-origin" },
      );
      return signed.json();
    }
    else {
      return undefined;
    }
  }

  async addAccessRequest(
    username,
    container,
    owner,
  ) {
    // Add a request for container access.
    let url = new URL("/request/user/".concat(username, "/", container),
      this.address);
    url.searchParams.append("owner", owner);

    let signed = await this._getSignature(
      60,
      "/request/user/".concat(username, "/", container),
    );

    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let resp = fetch(
      url, { method: "POST" },
    ).then(
      (resp) => { return resp.json(); },
    );
    return resp;
  }

  async listMadeRequests(
    username,
  ) {
    let url = new URL("/request/user/".concat(username),
      this.address);

    let signed = await this._getSignature(
      60,
      "/request/user/".concat(username),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let resp = fetch(
      url, { method: "GET" },
    ).then(
      (resp) => { return resp.json(); },
    );
    return resp;
  }

  async listOwnedRequests(
    username,
  ) {
    let url = new URL("/request/owner/".concat(username),
      this.address);

    let signed = await this._getSignature(
      60,
      "/request/owner/".concat(username),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let resp = fetch(
      url, { method: "GET" },
    ).then(
      (resp) => { return resp.json(); },
    );
    return resp;
  }

  async listContainerRequests(
    container,
  ) {
    let url = new URL("/request/container/".concat(container),
      this.address);

    let signed = await this._getSignature(
      60,
      "/request/container/".concat(container),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let resp = fetch(
      url, { method: "GET" },
    ).then(
      (resp) => { return resp.json(); },
    );
    return resp;
  }

  async shareDeleteAccess(
    username,
    container,
    owner,
  ) {
    // Delete the details of an existing share action.
    let url = new URL(
      "/request/user/".concat(username, "/", container), this.address,
    );
    url.searchParams.append("owner", owner);

    let signed = await this._getSignature(
      60,
      "/request/user/".concat(username, "/", container),
    );
    url.searchParams.append("valid", signed.valid);
    url.searchParams.append("signature", signed.signature);

    let deleted = fetch(
      url, { method: "DELETE" },
    ).then(
      (resp) => {
        if (resp.status == 200) { return true; }
        else { return false; }
      },
    );
    return deleted;
  }
}

export default SwiftSharingRequest;
