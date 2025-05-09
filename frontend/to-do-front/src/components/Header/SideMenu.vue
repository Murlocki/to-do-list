<script setup lang="ts">
import {useHeaderStore} from "@/store/headerStore.ts";
import icon from '@/assets/icon.svg'
import {useAuthStore} from "@/store/authStore.ts";
const headerStore = useHeaderStore();
const authStore = useAuthStore();
const elems = [
  {
    'id': 1,
    'link':'',
    'title':'Main',
    'icon':'mdi-home',
    'showBeforeLogin':true
  },
  {
    'id': 2,
    'link':'',
    'title':'Tasks',
    'icon':'mdi-post',
    'showBeforeLogin':true
  },
  {
    'id': 3,
    'link':'',
    'title':'Profile',
    'icon':'mdi-account',
    'showBeforeLogin':true
  }
]
</script>

<template>
  <v-navigation-drawer v-model="headerStore.menuIsOpen" temporary position-sticky class="w-auto h-auto" rail
                       rail-width="0">
    <v-list-item class="d-flex flex-column h-auto pa-3 bg-teal-accent-2">
      <template #prepend >
        <div class="w-auto h-auto">
          <v-img
              :src="icon"
              alt="Logo"
              class="mr-2 rounded-circle"
              max-width="120"
              max-height="120"
              width="100"
              height="100"
              aspect-ratio="1/1"
              cover
          />
        </div>
      </template>
      <v-list-item-title class="text-lg-h3 text-md-h4 text-h5 font-italic text-center">TO-DO app</v-list-item-title>
      <v-list-item-subtitle class="text-sm-h5 text-h6 py-2">App for your to-do-list</v-list-item-subtitle>
    </v-list-item>
    <div v-for="elem in elems">
      <v-list-item :id="elem.id" link :to="elem.link" class="py-2" density="compact">
        <template #prepend class="w-auto">
          <v-icon>{{ elem.icon }}</v-icon>
        </template>
        <v-list-item-title class="text-md-h4 text-h5" v-if="elem.showBeforeLogin">{{elem.title}}</v-list-item-title>
      </v-list-item>
      <v-divider></v-divider>
    </div>
    <template #append>
      <div class="w-100 h-100 pa-2">
        <v-btn size="x-large" class="w-100 bg-teal-darken-1 text-md-h4 test-h5" v-if="authStore.isLoggedIn">Logout</v-btn>
        <v-btn size="x-large" class="w-100 bg-teal-darken-1 text-md-h4 test-h5" v-if="!authStore.isLoggedIn">Login</v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<style scoped>

</style>