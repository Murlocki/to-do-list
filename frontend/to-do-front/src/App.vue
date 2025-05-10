<template>
  <v-app>
    <SideMenu />
    <Header />
    <v-main app>
      <v-container fluid class="pt-10 px-0 h-auto">
        <router-view></router-view>
      </v-container>
    </v-main>
    <v-footer app>
    </v-footer>
  </v-app>
</template>


<script setup lang="ts">
import Header from "@/components/Header/Header.vue";
import SideMenu from "@/components/Header/SideMenu.vue";
import MainPage from "@/components/MainPage/MainPage.vue";
</script>
