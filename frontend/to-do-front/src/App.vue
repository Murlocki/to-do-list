<template>
  <!-- App.vue -->

  <v-app>
    <SideMenu />
    <Header />

    <!-- Sizes your content based upon application components -->
    <v-main app>

      <!-- Provides the application the proper gutter -->
      <v-container fluid class="pt-10 px-0 h-auto">

        <!-- If using vue-router -->
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app>
      <!-- -->
    </v-footer>
  </v-app>
</template>


<script setup lang="ts">
import Header from "@/components/Header/Header.vue";
import SideMenu from "@/components/Header/SideMenu.vue";
import MainPage from "@/components/MainPage/MainPage.vue";
</script>
