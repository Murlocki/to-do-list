<script setup lang="ts">

import Header from "@/components/Header/Header.vue";
import SideMenu from "@/components/Header/SideMenu.vue";
</script>

<template>
  <v-app class="w-100">
    <SideMenu class="ma-0 pa-0"/>
    <Header class="h-auto"/>
    <v-main class="bg-blue w-100" style="height: 500px;"></v-main>
  </v-app>
</template>

<style scoped>

</style>
