<template>
  <div id="wrapper">
    <nav-bar></nav-bar>
    <side-bar></side-bar>
    <main-layout></main-layout>
  </div>
</template>

<script>
import NavBar from "@/components/NavBar";
import SideBar from "@/components/SideBar";
import Main from "@/components/Main";
export default {
  components: {
    "nav-bar": NavBar,
    "side-bar": SideBar,
    "main-layout": Main
  }
};
</script>
