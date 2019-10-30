<template>
  <!-- LEFT SIDEBAR -->
  <div id="sidebar-nav" class="sidebar">
    <div class="sidebar-scroll">
      <nav>
        <repos-items></repos-items>
        <projects-items></projects-items>
      </nav>
    </div>
  </div>
  <!-- END LEFT SIDEBAR -->
</template>


<script>
import ItemsWithDropdown from "@/components/ItemsWithDropdown";
import Projects from "@/components/Projects";

export default {
  name: "SideBar",
  components: {
    "repos-items": ItemsWithDropdown,
    "projects-items": Projects
  }
};
</script>

