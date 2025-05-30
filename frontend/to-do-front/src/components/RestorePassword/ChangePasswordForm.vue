<script setup lang="ts">

import {ref} from "vue";
import type {VForm} from "vuetify/components";
import {passwordRegex} from "@/regex.ts";
import {loginOut, updatePassword} from "@/externalRequests/requests.ts";
import {useRouter} from "vue-router";
import {useAuthStore} from "@/store/authStore.ts";

const router = useRouter();
const props = defineProps({
  token: String,
})

const valid = ref(false);
const form = ref<VForm | null>(null)
const password = ref('');
const repeatPassword = ref('');
const passwordRules = [
  (v: string): string | boolean => !!v || 'Password is required',
  (v: string): string | boolean => passwordRegex.test(v) || 'Password must be 8 characters, contains at least 1 uppercase and lowercase character,1 number and 1 of symbols:!@#$%^&*=',
]
const showPassword = ref(false)
const showPasswordRepeat = ref(false)
const error = ref("");
const loading = ref(false);
const authStore = useAuthStore();
const onSubmit = async () => {
  loading.value = true;
  if(password.value !== repeatPassword.value) {
    error.value = "Passwords must match";
    loading.value = false;
  }

  const isValid = await form.value?.validate()
  console.log(isValid?.valid)
  if (isValid?.valid) {
    const response: Response = await updatePassword(props.token,password.value);
    if(response.status === 200){
      if(authStore.isLoggedIn){
          authStore.clearToken()
      }
      await router.push('/login');
      loading.value = false;
      return;
    }

    const response_json = await response.json();
    error.value = response_json['detail']['message'];
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
              class="text-md-h3 text-sm-h4 text-h5">Write your new password</span>
      </div>
      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="password"
          label="Password"
          :type="showPassword ? 'text' : 'password'"
          :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showPassword = !showPassword"
          :rules="passwordRules"
          required
      ></v-text-field>
      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="repeatPassword"
          label="Password"
          :type="showPasswordRepeat ? 'text' : 'password'"
          :append-icon="showPasswordRepeat ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showPasswordRepeat = !showPasswordRepeat"
          :rules="passwordRules"
          required
      ></v-text-field>
      <div class="w-100 h-auto pa-2 d-flex align-center justify-center flex-column">
        <span v-if="error" class="text-h6 text-red mb-5">{{ error }}</span>
        <v-btn icon="mdi-account" class="w-lg-25 w-50 h-100 rounded-lg py-4 bg-teal-accent-3" @click="onSubmit"
               :loading="loading">Change password
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<style scoped>

</style>