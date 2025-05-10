<script setup lang="ts">
import {onMounted} from 'vue';
import {activateAccount} from "@/externalRequests/requests.ts";
import {ref} from 'vue';

const props = defineProps({
  token: {
    type: String,
    required: true
  }
})

const message = ref("Processing...")
const loading = ref(true)
onMounted(async () => {
  const response = await activateAccount(props.token);
  if(response.ok){
    message.value = "account activated successfully";
    loading.value = false;
  }
  else{
    const response_json = await response.json();
    message.value = response_json["detail"]["message"];
    loading.value = false;
  }
})
</script>

<template>
  <div style="min-width: 100vw;" class="d-flex align-center justify-center pa-md-0 px-2">
    <v-card class="pa-4 d-flex flex-column align-center transition" elevation="4">
      <span class="text-h4">{{message}}</span>
      <v-progress-circular indeterminate v-if="loading" size="large" class="mt-4"></v-progress-circular>
    </v-card>
  </div>
</template>

<style scoped>

</style>