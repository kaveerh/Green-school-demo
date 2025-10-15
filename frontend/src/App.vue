<template>
  <div id="app">
    <AppLayout>
      <RouterView />
    </AppLayout>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppLayout from './components/AppLayout.vue'
</script>

<style>
#app {
  font-family: Inter, system-ui, -apple-system, sans-serif;
}
</style>
