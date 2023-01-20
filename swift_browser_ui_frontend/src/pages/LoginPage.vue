<template>
  <div>
    <h2>Object browser login progress</h2>
    <p class="maintext">
      <br>The current login process requires logging in by fetching an
      unscoped token from the Openstack's keystone API. The server will handle
      scoping the token, logging in to the Openstack API, fetching all
      necessary information and revoking the token upon leaving the site.
      The login process currently goes as follows:
      <ol id="manlist">
        <li>
          Open a new tab and hit <b>F12</b> to open the console on said tab
        </li>
        <li>
          Open the <b>Network</b> tab on the console
        </li>
        <li>
          Open <b><a href="https://pouta.csc.fi:5001/v3/OS-FEDERATION/identity_providers/haka/protocols/saml2/auth">
            this link
          </a></b>
          in the new tab to begin authentication to Openstack and fetch an
          unscoped token.
        </li>
        <li>
          In the <b>Network</b> tab click open the last response visible on
          the console
        </li>
        <li>
          Copy the contents of the <b>X-Subject-Token</b> header from the
          response
        </li>
      </ol>
    </p>
    <p class="maintext">
      After successfully copying the response token id header, paste it in the
      following form's text field
    </p>
    <form
      id="retform"
      method="POST"
      action="/login/return"
    >
      <b>{{ formname }}</b><br>
      <input
        id="inputbox"
        class="formField"
        type="text"
        name="token"
      ><br>
      <input type="submit">
    </form>
    <div>
      <h2>Alternative login process</h2>
      <p class="maintext">
        Alternatively you can use this form to log in with a username
        and password.
      </p>
      <form
        id="classicform"
        method="POST"
        action="/login/credentials"
      >
        <b>{{ loginformname }}</b><br>
        <input
          class="formField"
          type="text"
          name="username"
        ><br>
        <input
          class="formField"
          type="password"
          name="password"
        ><br>
        <input type="submit">
      </form>
    </div>
  </div>
</template>

<style>
#loginwindow {
  width: 70ch;
  margin-left: auto;
  margin-right: auto;
  margin-top: 7%;
}

h2 {
  text-align: center;
}

.maintext {
  text-align: justify;
  line-height: 1.5;
}

#manlist {
  text-align: justify;
  line-height: 1.4;
}

li {
  text-align: left;
}

a {
  background: blueviolet;
  color: white;
}

a:hover {
  background: blue;
  color: white;
}

form {
  text-align: center;
  line-height: 2.5;
}

#inputbox {
  width: 40ch
}

.formField {
  width: 40ch;
}
</style>
