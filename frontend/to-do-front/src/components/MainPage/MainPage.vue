<script setup lang="ts">
  import image1 from '@/assets/1.jpeg'
  import image2 from '@/assets/2.jpg'
  import {useRouter} from 'vue-router'
  import {useAuthStore} from "@/store/authStore.ts";
  const authStore = useAuthStore();
  const images = [image1, image2]

  const router = useRouter()
  const registerPage = () => {
    router.push('/register')
  }
  const loginPage = () => {
    router.push('/login')
  }
</script>

<template>
  <div style="min-width: 100vw; height: 100%" class="px-6 w-100 d-flex flex-md-row flex-column align-center justify-center">
    <v-carousel show-arrows="hover" class="w-xl-50 w-md-75 h-auto w-100 pa-md-0 pa-2" cycle>
      <v-carousel-item v-for="image in images" :src="image" class="w-100 h-auto" cover
      >
        <v-img
            :src="image"
            cover
            class="w-100 h-100"
            aspect-ratio="1/1"
        />
      </v-carousel-item>
    </v-carousel>
    <div class="w-xl-50 h-xl-50 w-md-75 h-md-75 h-100 w-100 pa-5">
      <div class="d-flex flex-column align-center justify-center w-100 h-100">
        <div class="d-flex flex-column align-center ga-10">
          <span class="text-h2 font-italic font-weight-medium" style="font-family: 'JetBrains Mono',serif">To-Do Application</span>
          <span class="text-h4 font-italic">To do application for your daily to-do-plans. Plans your day ahead and track your progress between several devices.</span>
        </div>
        <div class="d-flex flex-sm-row flex-column justify-space-around w-100 h-md-50 h-100 mt-10 ga-5">
          <v-btn class="w-sm-50 w-100 h-100 pa-5 text-lg-h4 text-h5 rounded-xl bg-teal-darken-1" @click="loginPage" :disabled="authStore.isLoggedIn">Login</v-btn>
          <v-btn class="w-sm-50 w-100 h-100 pa-5 text-lg-h4 text-h5 rounded-xl bg-teal-accent-2" @click="registerPage" :disabled="authStore.isLoggedIn">Register</v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>