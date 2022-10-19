<template>
  <div id="c-footer">
    <div class="">
      <div class="navbar-menu">
        <div class="navbar-start">
          <div class="col-3">
            <div class="row">
              <span class="largetext">
              {{ $t("message.footerMenu.groupandprogram") }}
            </span>
            </div>
            <div class=" row smalltext">
              {{ $t("message.devel") }}
              <a class="linktext"
              href="https://csc.fi"
              :alt="$t('message.footerMenu.csc')"
            >{{
              $t("message.footerMenu.csc")
            }}</a>
            </div>
          </div>        
        </div>
        <div class="navbar-end">
          <div class="navbar-item smalltext">
            <a class="linktext"
              href="https://research.csc.fi/-/sd-connect"
              :alt="$t('message.footerMenu.servicedescription')"
            >{{
              $t("message.footerMenu.servicedescription")
            }}</a>
          </div> 
          <div class="navbar-item smalltext">
            <p>{{ $t("message.footerMenu.accessibility") }}</p> 
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name:"CFooter",
};
</script>

<style lang="scss" scoped>
@import "@/css/prod.scss";

#c-footer{
  flex-shrink: 0;
  height: 130px;
  width: 100%;
  padding:40px 60px;
  background-color:#DFE1E3;
  margin-top:40px; 
}
.largetext{
  font-family: 'Museo Sans';
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: #595959;
}
.smalltext{
  font-family: 'Museo Sans';
  font-style: normal;
  font-weight: 400;
  font-size: 14px;
  line-height: 18px;
  color: #595959;
}
.linktext {
  color: #595959; 
}

</style>
