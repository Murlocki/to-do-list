<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useAuthStore } from "@/store/authStore.ts";
import { getAllTasks } from "@/externalRequests/requests.ts";
import { useRouter } from "vue-router";
import { useTaskStore } from "@/store/taskStore.ts";
import Task from "@/models/Task.ts";

const authStore = useAuthStore();
const taskStore = useTaskStore();
const router = useRouter();
const loading = ref(false);
onMounted(async () => {
  loading.value = true;
  const response = await getAllTasks(authStore.token);
  if (response.status === 401 || response.status === 403) {
    authStore.clearToken();
    await router.push("/login");
    loading.value = false;
    return
  }
  const response_json = await response.json();
  console.log(response_json);
  console.log(response_json["token"]);
  console.log(response_json["data"]);
  await authStore.setToken(response_json["token"]);
  await taskStore.fetchTasks(response_json["data"]);
  loading.value = false;
})

// Заглушка для создания новой задачи
function addTask() {
  // Здесь можно открыть модальное окно с формой или сразу добавить новую задачу
  // Например, добавим пустую задачу в список (для демонстрации)
  const newTask = new Task(
      Date.now(), // id
      "New Task",
      null,
      0, // статус (например, IN_PROGRESS)
      1, // userId (пример)
      null
  );
  taskStore.$state.tasks.unshift(newTask); // добавляем в начало списка
  // Можно добавить логику редактирования сразу после создания
}
</script>

<template>
  <div style="min-width: 100vw;" class="d-flex flex-column align-center justify-center pa-md-0 px-2">
    <v-card class="w-md-75 w-100 d-flex flex-column align-center justify-center py-2">
      <div class="py-4 bg-teal-accent-3 w-100 d-flex align-center justify-space-evenly flex-row mb-4">
        <span class="text-h4 font-italic" style="font-family: 'JetBrains Mono',serif">Your to-do list</span>
        <v-btn
            class="bg-teal-darken-1"
            rounded
            @click="addTask"
            aria-label="Add new task"
        >
          <v-icon left>mdi-plus</v-icon>
        </v-btn>
      </div>

      <v-virtual-scroll
          :items="taskStore.$state.tasks"
          class="w-100 h-auto"
          :loading="loading"
      >
        <template #default="{ item }">
          <v-card class="pa-3 mb-2" outlined>
            <v-row align="center" justify="space-between" no-gutters>
              <v-col cols="auto">
                <v-checkbox
                    :aria-label="`Mark ${(item as Task).title} as completed`"
                    @change="toggleCompleted(item)"
                />
              </v-col>

              <v-col>
                <div class="text-md-h5 text-h6">{{ (item as Task).title }}</div>
                <div class="text-md-body-1 text-body-2 text--secondary text-break">FFPFPEPFEPFPFPEFPEPFEPFPEPEFPFPFPEPFPFP</div>
                <div class="text-md-body-1 text-body-2 text--secondary">{{ (item as Task).prettyFulfilledDate }}</div>
              </v-col>

              <v-col cols="auto" class="d-flex flex-column gap-4 h-100">
                <v-btn icon @click="editTask(item)" aria-label="Edit task">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn icon @click="deleteTask(item)" aria-label="Delete task">
                  <v-icon color="red">mdi-delete</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </template>
      </v-virtual-scroll>
      <v-progress-linear
          v-if="loading"
          indeterminate
          class="bg-teal-darken-1"
          height="5"
      />
    </v-card>
  </div>
</template>
