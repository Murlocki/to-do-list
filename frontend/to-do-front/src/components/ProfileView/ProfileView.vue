<script setup lang="ts">
import {onMounted, ref} from "vue";
import {useAuthStore} from "@/store/authStore.ts";
import {getUserProfile} from "@/externalRequests/requests.ts";
import {useRouter} from "vue-router";
import {useUserStore} from "@/store/userStore.ts";
import {UserDTO} from "@/models/UserDTO.ts";

const router = useRouter();
const authStore = useAuthStore();
const userStore = useUserStore();
const loading = ref(false);
const error = ref("");
onMounted(async () => {
  loading.value = true;
  const token = authStore.token;
  console.log(token);
  const response = await getUserProfile(token)
  if (response.status === 401) {
    authStore.clearToken();
    await router.push("/login");
    loading.value = false;
    return
  }
  if (response.status === 200) {
    console.log(response)
    const response_json = await response.json()
    authStore.setToken(response_json["token"]);
    console.log(response_json);
    userStore.setUser(new UserDTO(
        response_json["data"]["id"],
        response_json["data"]["email"],
        response_json["data"]["firstName"],
        response_json["data"]["lastName"],
        response_json["data"]["username"]
    ));
    console.log(userStore.user)
    loading.value = false;
  }
})
function onResetPassword(){
  const token = authStore.token;
  router.push(`/login/forgot-password/${token}`);
}
</script>

<template>
  <v-dialog v-model="loading">
    <v-progress-linear :loading="loading" height="40" indeterminate></v-progress-linear>
  </v-dialog>
  <div style="min-width: 100vw;" class="d-flex flex-column align-center justify-center pa-md-0 px-2">
    <v-card class="w-md-50 w-sm-75 w-100 d-flex flex-column align-center justify-center py-2" v-if="!loading">
      <div class="py-4 bg-teal-accent-3 w-100 d-flex align-center justify-space-between flex-row mb-4">
        <span class="text-h4 font-italic text-center flex-grow-1" style="font-family: 'JetBrains Mono',serif;">
          Your to-do profile
        </span>
      </div>

      <div v-if="error">
        <span class="text-error text-h3">{{ error }}</span>
      </div>
      <div v-if="!loading" class="w-100 px-2 d-flex flex-column ga-5 text-center">
        <div class="border-b-lg w-100 text-sm-h5 text-h6">
          <span>{{ (userStore.user as UserDTO)?.username }}</span>
        </div>
        <div class="border-b-lg w-100 text-sm-h5 text-h6">
          <span>{{ (userStore.user as UserDTO)?.firstName }}</span>
        </div>
        <div class="border-b-lg w-100 text-sm-h5 text-h6">
          <span>{{ (userStore.user as UserDTO)?.lastName }}</span>
        </div>
        <div class="border-b-lg w-100 text-sm-h5 text-h6">
          <span>{{ (userStore.user as UserDTO)?.email }}</span>
        </div>
      </div>
      <div class="d-flex flex-row mt-10 w-100 pl-4 pr-4 ga-3">
        <v-btn size="x-large" class="bg-teal-accent-3 flex-grow-1" @click="onResetPassword">
          Update password
        </v-btn>
      </div>
    </v-card>
  </div>
</template>
