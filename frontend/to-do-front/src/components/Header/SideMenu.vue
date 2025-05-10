<script setup lang="ts">
import {useHeaderStore} from "@/store/headerStore.ts";
import icon from '@/assets/icon.svg'
import {useAuthStore} from "@/store/authStore.ts";
import {useRouter} from "vue-router";
import {loginOut} from "@/externalRequests/requests.ts";
import {ref} from "vue";
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

const router = useRouter();
const isLoading = ref(false);
const logoutFunction = async function (){
  isLoading.value = true;
  const token = authStore.$state.token;
  const response = await loginOut(token);
  if(response.status === 200){
    authStore.clearToken()
    await router.push('/');
  }
  await headerStore.changeMenuStatus(false);
  isLoading.value = false;
}
</script>

<template>
  <v-navigation-drawer v-model="headerStore.menuIsOpen" temporary class="w-auto h-auto" rail
                       rail-width="0" app>
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
      <v-list-item-title class="text-lg-h3 text-md-h4 text-h5 text-center font-italic" style="font-family: 'JetBrains Mono',serif">To Do app</v-list-item-title>
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
        <v-btn size="x-large" class="w-100 bg-teal-darken-1 text-md-h4 test-h5" v-if="authStore.isLoggedIn" @click="logoutFunction" :loading="isLoading">Logout</v-btn>
        <v-btn size="x-large" class="w-100 bg-teal-darken-1 text-md-h4 test-h5" v-if="!authStore.isLoggedIn" @click="router.push('/login')">Login</v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<style scoped>

</style>