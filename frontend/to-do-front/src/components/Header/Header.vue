<script setup lang="ts">
import icon from "@/assets/icon.svg"
import {useHeaderStore} from "@/store/headerStore.ts";
import {useAuthStore} from "@/store/authStore.ts";
import '@/style.css'
const headerStore = useHeaderStore();
const authStore = useAuthStore();
</script>

<template>
  <v-app-bar :elevation="2" app class="bg-teal-accent-2 py-2 " height="100">
    <template v-slot:prepend>
      <v-app-bar-nav-icon size="x-large" @click="headerStore.changeMenuStatus(true)" />
    </template>

    <v-app-bar-title height="auto">
      <div class="d-flex align-center h-100" >
        <v-img
            :src="icon"
            alt="Logo"
            class="rounded-circle me-4 "
            max-width="100"
            max-height="100"
            style="object-fit: fill"
        />
        <span class="text-lg-h3 text-md-h4 text-h5 font-italic" style="font-family: 'JetBrains Mono',serif">To Do App</span>
      </div>
    </v-app-bar-title>

    <template v-slot:append>
      <v-tooltip class="text-h3" text="Login">
        <template #activator="{ props }">
          <v-btn icon size="x-large" v-if="!authStore.isLoggedIn" v-bind="props">
            <v-icon size="x-large">mdi-account-plus</v-icon>
          </v-btn>
        </template>
      </v-tooltip>
      <v-tooltip text="Logout">
        <template #activator="{ props }">
          <v-btn icon size="x-large" v-if="authStore.isLoggedIn" v-bind="props">
            <v-icon size="x-large">mdi-account</v-icon>
          </v-btn>
        </template>
      </v-tooltip>
    </template>
  </v-app-bar>

</template>

<style scoped>
</style>