<script setup lang="ts">
import {onMounted, ref} from 'vue';
import {nameRegex, emailRegex, passwordRegex, userNameRegex} from "@/regex.ts";
import type { VForm } from 'vuetify/components';
import {UserCreate} from "@/models/UserCreate.js";
import {registerUser} from "@/externalRequests/requests.ts";
import {useRouter} from "vue-router";
import {useAuthStore} from "@/store/authStore.ts";

const router = useRouter()
const store = useAuthStore();
onMounted(async () => {
  console.log(store.isLoggedIn);
  if (store.isLoggedIn) {
    await router.push("/");
  }
})

const valid = ref(false);
const form = ref<VForm | null>(null)
// Для имен
const firstName = ref('');
const lastName = ref('');
const nameRules = [
  (v: string): string | boolean => !!v || 'Name is required',
  (v: string): string | boolean => nameRegex.test(v) || 'Name must contain only alphabetic characters',
]

//Для почты
const email = ref('');
const emailRules = [
  (v: string): string | boolean => !!v || 'Email is required',
  (v: string): string | boolean => emailRegex.test(v) || 'Email must be a valid email address',
]

const password = ref('');
const passwordRules = [
  (v: string): string | boolean => !!v || 'Password is required',
  (v: string): string | boolean => passwordRegex.test(v) || 'Password must be 8 characters, contains at least 1 uppercase and lowercase character,1 number and 1 of symbols:!@#$%^&*=',
]
const showPassword = ref(false)

const userName = ref('');
const userNameRules = [
  (v: string): string | boolean => !!v || 'Username is required',
  (v: string): string | boolean => userNameRegex.test(v) || 'Username must be a valid',
]

const error = ref("");
const loading = ref(false);
const onSubmit = async () => {
  loading.value = true;
  const isValid = await form.value?.validate()
  console.log(isValid?.valid)
  if (isValid?.valid) {
    const user: UserCreate = new UserCreate(email.value, firstName.value, lastName.value, userName.value, password.value);
    const response: Response = await registerUser(user);
    if(response.status === 201){
      await router.push('/login');
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
    <v-form v-model="valid" class="d-flex flex-column align-center pa-md-4 pa-2 ga-4 elevation-4 w-lg-50 w-md-75 w-100" style="border-radius: 100px" ref="form">
      <div class="bg-teal-darken-1 rounded-pill pa-4 my-6">
        <span style="font-family: 'JetBrains Mono',serif" class="text-md-h3 text-sm-h4 text-h5">Register your to-do-list</span>
      </div>
      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="userName"
          label="Username"
          :rules="userNameRules"
          required
      ></v-text-field>

      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="firstName"
          :rules="nameRules"
          label="First name"
          required
      ></v-text-field>


      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="lastName"
          :rules="nameRules"
          label="Last name"
          required
      ></v-text-field>

      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="email"
          :rules="emailRules"
          label="E-mail"
          type="email"
          required
      ></v-text-field>


      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="password"
          :rules="passwordRules"
          label="Password"
          :type="showPassword ? 'text' : 'password'"
          :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showPassword = !showPassword"
          required
      ></v-text-field>
      <div class="w-100 h-auto pa-2 d-flex align-center justify-center flex-column">
        <span v-if="error" class="text-h6 text-red mb-5">{{error}}</span>
        <v-btn icon="mdi-account" class="w-lg-25 w-50 h-100 rounded-lg py-4 bg-teal-accent-3" @click="onSubmit" :loading="loading">Register</v-btn>
      </div>
    </v-form>
  </div>
</template>

<style scoped>

</style>