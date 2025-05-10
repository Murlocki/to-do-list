<script setup lang="ts">
import {onMounted, ref} from 'vue';
import type {VForm} from 'vuetify/components';
import {loginUser} from "@/externalRequests/requests.ts";
import {useRouter} from "vue-router";
import {UAParser} from 'ua-parser-js';
import AuthForm from "@/models/AuthForm.ts";
import {useAuthStore} from "@/store/authStore.ts";

const router = useRouter()
const authStore = useAuthStore();
onMounted(() => {
  console.log(authStore.isLoggedIn);
  if (authStore.isLoggedIn) {
    router.push("/");
  }
})
const valid = ref(false);
const form = ref<VForm | null>(null)


const password = ref('');
const showPassword = ref(false)
const identifier = ref('');
const ip= ref("")
const device = ref("")
const remember = ref(false)

const error = ref("");
const loading = ref(false);
const onSubmit = async () => {
  loading.value = true;
  const isValid = await form.value?.validate()
  if (isValid?.valid) {

    const responseIp = await fetch('https://api.ipify.org?format=json')
    if (responseIp.ok) {
      const res = await responseIp.json()
      ip.value = res["ip"];
      console.log('IP пользователя:', ip.value);
    }
    const parser = new UAParser();
    device.value = parser.getResult()!.browser!.name!;
    console.log('Информация об устройстве:', device.value);


    const authForm: AuthForm = new AuthForm(identifier.value, password.value, device.value, ip.value, remember.value);
    const response: Response = await loginUser(authForm);
    if (response.status === 200) {
      const response_json = await response.json();
      authStore.setToken(response_json["token"]);
      await router.push('/');
      loading.value = false;
      return;
    }

    const response_json = await response.json();
    error.value = response_json['detail'];
    console.log(response_json);
  } else {
    error.value = "Please correct the errors above."
  }
  loading.value = false;
}
</script>

<template>
  <div style="min-width: 100vw;" class="d-flex align-center justify-center pa-md-0 px-2">
    <v-form v-model="valid" class="d-flex flex-column align-center pa-md-4 pa-2 ga-4 elevation-4 w-lg-50 w-md-75 w-100"
            style="border-radius: 100px" ref="form">
      <div class="bg-teal-darken-1 rounded-pill pa-4 my-6">
        <span style="font-family: 'JetBrains Mono',serif"
              class="text-md-h3 text-sm-h4 text-h5">Login in your to-do life</span>
      </div>
      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="identifier"
          label="Identifier"
          required
      ></v-text-field>
      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="password"
          label="Password"
          :type="showPassword ? 'text' : 'password'"
          :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showPassword = !showPassword"
          required
      ></v-text-field>
      <v-checkbox class="text-h6" label="Remember me" v-model="remember"></v-checkbox>
      <div class="w-100 h-auto pa-2 d-flex align-center justify-center flex-column">
        <span v-if="error" class="text-h6 text-red mb-5">{{ error }}</span>
        <v-btn icon="mdi-account" class="w-lg-25 w-50 h-100 rounded-lg py-4 bg-teal-accent-3" @click="onSubmit"
               :loading="loading">Login
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<style scoped>

</style>