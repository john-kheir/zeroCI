<template>
  <!-- NAVBAR -->
  <nav class="navbar navbar-default navbar-fixed-top">
    <div class="brand">
      <a href="/" class="text-uppercase">
        <img :src="img" alt="TFT Logo" class="img-responsive logo" />
      </a>
    </div>
    <div class="container-fluid">
      <div class="navbar-btn">
        <button type="button" class="btn-toggle-fullwidth">
          <i class="lnr lnr-arrow-left-circle"></i>
        </button>
      </div>
    </div>
  </nav>
  <!-- END NAVBAR -->
</template>

<script>
export default {
  name: "NavBar",
  data() {
    return {
      img: "/static/assets/img/tft.png"
    };
  }
};
</script>
