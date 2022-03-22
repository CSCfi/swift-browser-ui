<template>
  <c-main>
    <c-toolbar class="relative">
      <c-csc-logo />
      {{ $t('message.program_name') }}
      <c-spacer />
    </c-toolbar>
    <c-row>
      <c-flex>
        <c-container class="padding">
          <c-card>
            <c-card-content>
              <h2>{{ $t('message.program_name') }}</h2>
              <p>{{ $t('message.program_description') }}</p>
            </c-card-content>
            <c-card-actions>
              <c-button
                size="large"
                :loading="loading"
                :disabled="!idb"
                @click="loginButtonClick"
              >
                {{ $t('message.indexOIDC.logIn') }}
              </c-button>
            </c-card-actions>
            <c-card-content v-if="!idb">
              <p>
                <strong>{{ $t('message.error.idb') }}</strong>
              </p>
            </c-card-content>
          </c-card>
        </c-container>
      </c-flex>
    </c-row>
    <footer>
      <c-container>
        <c-flex>
          <div>
            <h5>CSC - IT Center for Science Ltd.</h5>
            <p>P.O. Box 405 FI-02101 Espoo, Finland</p>
            <p>+358 9 457 2001</p>
          </div>
          <div>
            <h5>Service Desk</h5>
            <p>Open Monday to Friday from 8.30 a.m. to 4 p.m.</p>
            <p>+358 9 457 2821</p>
            <p>servicedesk@csc.fi</p>
          </div>
        </c-flex>
      </c-container>
    </footer>
  </c-main>
</template>

<style>
c-card {
  margin: 2rem auto;
  padding: 7rem 5rem 5rem;
  max-width: 55rem;
  height: 35rem;
  background-image: url(@/assets/banner_login.png);
  background-size: cover;
  background-repeat: no-repeat;
  background-color: var(--white);
}
c-card-content h2 {
  color: var(--csc-primary);
  font-weight: 700;
  font-size: 1.5rem;
  text-transform: uppercase;
}
c-card-content p {
  color: var(--csc-dark-grey);
  font-weight: 300;
}
c-button {
  margin-top: 2rem;
}
footer {
  background-color: var(--csc-light-grey);
  color: var(--csc-dark-grey);
  padding: 1rem 0 1rem;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
}
footer h5 {
  font-weight: bold;
}
footer p {
  font-size: 0.875rem;
  line-height: 1rem;
}
footer c-flex {
  display: flex;
  justify-content: space-around;
  text-align: center;
}
</style>
