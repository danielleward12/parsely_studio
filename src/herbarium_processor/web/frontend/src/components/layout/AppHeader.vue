<template>
  <AppBar badge-text="1.0.0">
    <template #right>
      <ul class="menu menu-horizontal px-1">
        <li>
          <RouterLink
            class="rounded-btn"
            to="/how-it-works"
          >
            How it works
          </RouterLink>
        </li>
        <li>
          <RouterLink
            class="rounded-btn"
            to="/about"
          >
            Our mission
          </RouterLink>
        </li>
      </ul>
    </template>
  </AppBar>
</template>

<script setup>
import { RouterLink } from "vue-router"
import AppBar from "@/components/layout/AppBar.vue";
</script>

<style scoped>
/* ... */
</style>
