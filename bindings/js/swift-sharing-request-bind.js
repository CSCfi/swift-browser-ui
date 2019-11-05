// Swift cross account container sharing API JavaScript bindings module.

class SwiftSharingRequest {
// Swift sharing request backend client.

  constructor (
      address
  ) {
      this.address = address;
  }

  async addAccessRequest(
      username,
      container,
      owner
  ) {
    // Add a request for container access.
    let url = new URL("/request/user/".concat(username, "/", container),
                      this.address);
    url.searchParams.append("owner", owner);

    let resp = fetch(
      url, {method: "POST"}
    ).then(
      (resp) => {return resp.json();}
    );
    return resp;
  }

  async listMadeRequests(
    username
  ) {
    let url = new URL("/request/user/".concat(username));
    let resp = fetch(
      url, {method: "GET"}
    ).then(
      (resp) => {return resp.json();}
    );
    return resp;
  }

  async listOwnedRequests(
    username
  ) {
    let url = new URL("/request/owner/".concat(username));
    let resp = fetch(
      url, {method: "GET"}
    ).then(
      (resp) => {return resp.json();}
    );
    return resp;
  }

  async listContainerRequests(
    container
  ) {
    let url = new URL("/request/container/".concat(container));
    let resp = fetch(
      url, {method: "GET"}
    ).then(
      (resp) => {return resp.json();}
    );
    return resp;
  }

  async shareDeleteAccess(
      username,
      container,
      owner
  ) {
    // Delete the details of an existing share action.
    let url = new URL(
    "/request/user/".concat(username, "/", container), this.address
    );
    url.searchParams.append("owner", owner);
    let deleted = fetch(
      url, {method: "DELETE"}
    ).then(
      (resp) => {
        if (resp.status == 200) {return true;}
        else {return false;}
      }
    );
    return deleted;
  }    
}

export default SwiftSharingRequest;
