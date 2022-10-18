<template>
    <div id="c-footer">
    <div class="">
          <p>
            <span class="leftmenu">
              {{ $t("message.footerMenu.groupandprogram") }}
            </span>
            {{ $t("message.devel") }}
            </p>
            <p>
            <a
              href="https://csc.fi"
              :alt="$t('message.footerMenu.csc')"
            >{{
              $t("message.footerMenu.csc")
            }}</a>
          </p>
        </div>
        <div>
          <p>
            <span class="rightmenu">
              {{ $t("message.footerMenu.servicedescription") }}
            </span>
          </p>
          <p>{{ $t("message.footerMenu.accessibility") }}</p>
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
  padding:40px 60px 40px ;
  background-color:#DFE1E3;
  margin-top:40px;
  color: #595959;
  font: Museo Sans;
  
}
.leftmenu{
  text-align:left;
}
.rightmenu{
  text-align: right;
}
</style>
