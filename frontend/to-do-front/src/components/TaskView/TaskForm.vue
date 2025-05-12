<script setup lang="ts">

import {useTaskFormStore} from "@/store/taskFormStore.ts";
import type {VForm} from "vuetify/components";
import {ref, defineEmits} from "vue";
import TaskUpdate from "@/models/TaskUpdate.ts";
import {createNewTask} from "@/externalRequests/requests.ts";
import {useAuthStore} from "@/store/authStore.ts";


const taskFormStore = useTaskFormStore();
const authStore = useAuthStore();
const valid = ref(false);
const form = ref<VForm | null>(null)
const titleRules = [
  (v: string): string | boolean => !!v || 'Title is required'
];

const emit = defineEmits(['task-added'])
const loading = ref(false);
const error = ref("")
async function onSubmit() {
  loading.value = true;
  const isValid = await form.value?.validate()
  if (!isValid?.valid) {
    error.value = "Please correct the errors above."
    loading.value = false
    return;
  }
  console.log(taskFormStore.title);
  console.log(taskFormStore.description);
  console.log(taskFormStore.fulfilledDate);
  console.log(taskFormStore.time)
  console.log(taskFormStore.fullDate);
  const newTask = new TaskUpdate(taskFormStore.title, taskFormStore.description);
  newTask.fulfilledDate = taskFormStore.fullDate;
  console.log(newTask);
  const response = await createNewTask(newTask,authStore.token);
  const response_json = await response.json();
  if(response.status === 201) {
    console.log(response_json);
    authStore.setToken(response_json["token"]);
    loading.value = false;
    await taskFormStore.setIsOpen(false);
    emit("task-added");
    return;
  }

  error.value = response_json["detail"]["message"];
  authStore.setToken(response_json["detail"]["token"]);
  loading.value = false;
}

function onReset() {
  taskFormStore.title = "";
  taskFormStore.description = null;
  taskFormStore.fulfilledDate = null;
  taskFormStore.time = null;
  taskFormStore.setIsOpen(false)
}

const timePicker = ref(false)
</script>

<template>
  <v-card class="w-100 px-2">
    <v-form v-model="valid" class="d-flex flex-column align-center ga-4 w-100 " style="border-radius: 100px" ref="form">
      <div class="bg-teal-darken-1 rounded-pill pa-4 my-6">
        <span style="font-family: 'JetBrains Mono',serif"
              class="text-md-h3 text-sm-h4 text-h5">Add task to your to-do</span>
      </div>
      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="taskFormStore.$state.title"
          label="Title"
          required
          :rules="titleRules"
      ></v-text-field>

      <v-text-field
          class="w-sm-75 w-100"
          rounded="pill"
          v-model="taskFormStore.$state.description"
          label="Description"
          required
      ></v-text-field>

      <v-date-picker show-adjacent-months
                     required
                     v-model="taskFormStore.$state.fulfilledDate"
                     mode="dateTime"
                     is24hr
                     :minute-increment="5">
        <template v-slot:actions>
          <v-btn text @click="taskFormStore.$state.fulfilledDate = null;">Clear</v-btn>
        </template>
      </v-date-picker>
      <div class="w-sm-75 w-100 px-2">
        <v-text-field
            v-model="taskFormStore.$state.time"
            :active="timePicker"
            :focus="timePicker"
            label="Pick a time"
            prepend-icon="mdi-clock-time-four-outline"
            readonly
            :disabled="taskFormStore.isDatePresent"

        >
          <v-menu
              v-model="timePicker"
              :close-on-content-click="false"
              activator="parent"
              transition="scale-transition"
          >
            <v-time-picker
                v-if="timePicker"
                v-model="taskFormStore.$state.time"
                full-width
            >
              <template v-slot:actions>
                <div class="w-100 d-flex flex-row justify-space-evenly">
                  <v-btn text @click="timePicker=false">Ok</v-btn>
                  <v-btn text @click="taskFormStore.$state.time = null;">Clear</v-btn>
                </div>
              </template>
            </v-time-picker>
          </v-menu>
        </v-text-field>
      </div>

      <div class="w-100 h-auto pa-2 d-flex align-center justify-center flex-column">
        <span v-if="error" class="text-h6 text-red mb-5">{{error}}</span>
        <div class="w-100 d-flex flex-row justify-space-between">
          <v-btn icon="mdi-account" class="w-lg-25 w-50 h-100 rounded-lg py-4 bg-teal-accent-3"
                 @click="onSubmit"
                 :loading="loading"
                 :disabled="loading"
                 >Register
          </v-btn>
          <v-btn
              class="w-lg-25 w-50 h-100 rounded-lg py-4"
              text="Close Dialog"
              @click="onReset"
              :disabled="loading"
          ></v-btn>
        </div>
      </div>
    </v-form>
  </v-card>

</template>

<style scoped>

</style>