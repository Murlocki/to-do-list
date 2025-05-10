<script setup lang="ts">

import {ref} from "vue";
import {emailRegex} from "@/regex.ts";
import {getForgotEmail} from "@/externalRequests/requests.ts";

const email = ref('');
const emailRules = [
  (v: string): string | boolean => !!v || 'Email is required',
  (v: string): string | boolean => emailRegex.test(v) || 'Email must be a valid email address',
]

const error = ref('')
const ok=ref(false)
const loading = ref(false)
const onSubmit = async () => {
  loading.value = true
  const response = await getForgotEmail(email.value);
  ok.value = false;
  if(response.status === 200) {
    ok.value = true;
  }
  else {
    const json_response = await response.json()
    error.value = json_response["detail"];
  }
  loading.value = false
}

</script>

<template>
  <div style="min-width: 100vw;" class="d-flex align-center justify-center pa-md-0 px-2">
    <v-form class="d-flex flex-column align-center pa-md-4 pa-2 ga-4 elevation-4 w-lg-50 w-md-75 w-100"
            style="border-radius: 100px" ref="form">
      <div class="bg-teal-darken-1 rounded-pill pa-4 my-6">
        <span style="font-family: 'JetBrains Mono',serif"
              class="text-md-h2 text-sm-h3 text-h4">Reset password</span>
      </div>
      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="email"
          :rules="emailRules"
          label="E-mail"
          type="email"
          required
      ></v-text-field>
      <div class="w-100 h-auto pa-2 d-flex align-center justify-center flex-column">
          <span class="text-h6 font-italic mb-5">Write your account email</span>
      </div>
      <div class="w-100 h-auto pa-2 d-flex align-center justify-center flex-column">
        <span v-if="error" class="text-h6 text-red mb-5">{{ error }}</span>
        <span v-if="ok" class="text-h6 text-red mb-5">Send mail on your email</span>
        <v-btn icon="mdi-account" class="w-lg-25 w-50 h-100 rounded-lg py-4 bg-teal-accent-3" @click="onSubmit"
               :loading="loading">Get email
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<style scoped>

</style>