<script setup lang="ts">
import {onMounted, ref, reactive} from "vue";
import {useAuthStore} from "@/store/authStore.ts";
import {deleteTaskById, getAllTasks, updateTaskById} from "@/externalRequests/requests.ts";
import {useRouter} from "vue-router";
import {useTaskStore} from "@/store/taskStore.ts";
import Task from "@/models/Task.ts";
import TaskUpdate from "@/models/TaskUpdate.ts";
import {Status} from "@/models/Task.ts"
import {useTaskFormStore} from "@/store/taskFormStore.ts";
import TaskForm from "@/components/TaskView/TaskForm.vue";


const authStore = useAuthStore();
const taskStore = useTaskStore();
const router = useRouter();
const loading = ref(false);
const tasksKey = ref(0)
async function loadTasks(){
  await taskStore.clearTasks()
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
  for (const key in scrollerRefs) {
    delete scrollerRefs[key]
  }
  taskStore.$state.tasks.forEach((item: Task) => {
    scrollerRefs[item.id] = {
      checked: item.status === Status.COMPLETED,
    }
  })
  console.log(scrollerRefs)
  loading.value = false;
  tasksKey.value = (tasksKey.value+1)%2
}
onMounted(loadTasks);

type ScrollerRef = {
  checked: boolean
}

const scrollerRefs = reactive<Record<number, ScrollerRef>>({})

function getRef(taskId: number) {
  return scrollerRefs[taskId] ?? {checked: false};
}

const error = ref('');

async function toggleComplete(task: Task) {
  const refItem = scrollerRefs[task.id];
  if (!refItem) return;

  loading.value = true;
  try {
    const taskUpdate = new TaskUpdate(
        task.title,
        task.description,
        refItem.checked ? Status.COMPLETED : Status.IN_PROGRESS,
        task.fulfilledDate,
        task.version
    );
    console.log(taskUpdate);
    const response = await updateTaskById(task.id, taskUpdate, authStore.token);
    const response_json = await response.json();

    if (response.ok) {
      await authStore.setToken(response_json.token);
      error.value = "";
      taskUpdate.version = response_json["data"]["version"];
      await taskStore.updateTaskById(task.id, taskUpdate);
    } else if (response.status === 401 || response.status === 403) {
      authStore.clearToken();
      await router.push("/");
    } else {
      authStore.setToken(response_json.detail?.token);
      refItem.checked = !refItem.checked;
      error.value = response_json.detail?.error || "Unknown error";
    }
  } catch (e) {
    console.error("Ошибка при обновлении задачи:", e);
    error.value = "Ошибка сети или сервера";
  } finally {
    loading.value = false;
  }
}


async function deleteTask(id: number) {
  const refItem = scrollerRefs[id];
  if (!refItem) return;

  loading.value = true;
  await taskStore.clearTasks()
  try {
    const response = await deleteTaskById(id, authStore.token);
    const response_json = await response.json();

    if (response.ok) {
      await authStore.setToken(response_json.token);
      error.value = "";
      await loadTasks()
    } else if (response.status === 401 || response.status === 403) {
      authStore.clearToken();
      await router.push("/");
    } else {
      authStore.setToken(response_json.detail?.token);
      error.value = response_json.detail?.error || "Unknown error";
    }
  } catch (e) {
    console.error("Ошибка при обновлении задачи:", e);
    error.value = "Network or server error";
  } finally {
    loading.value = false;
  }
}

const taskFormStore = useTaskFormStore();
async function toggleUpdate(id: number) {
  const task = taskStore.getTaskById(id);
  console.log(id)
  console.log(task);
  await taskFormStore.setTask(task);
  await taskFormStore.setIsOpen(true);
}

</script>

<template>
  <v-dialog v-model="taskFormStore.isOpen" class="d-flex align-center justify-center w-lg-50 w-md-75 w-100">
    <TaskForm @task-added="loadTasks" :is-update="taskFormStore.isUpdating"/>
  </v-dialog>
  <v-dialog v-model="loading">
    <v-progress-linear :loading="loading" height="40" indeterminate></v-progress-linear>
  </v-dialog>
  <div style="min-width: 100vw;" class="d-flex flex-column align-center justify-center pa-md-0 px-2">
    <v-card class="w-md-75 w-100 d-flex flex-column align-center justify-center py-2">
      <div class="py-4 bg-teal-accent-3 w-100 d-flex align-center justify-space-between flex-row mb-4">
        <!-- Пустой блок слева для балансировки -->
        <div style="width: 48px;"></div>
        <span class="text-h4 font-italic text-center flex-grow-1" style="font-family: 'JetBrains Mono',serif;">
          Your to-do list
        </span>
        <v-btn
            class="bg-teal-darken-1"
            rounded
            aria-label="Add new task"
            @click="taskFormStore.setIsOpen(true)"
            text="Open Dialog"
        >
          <v-icon left>mdi-plus</v-icon>
        </v-btn>
      </div>

      <div v-if="error">
        <span class="text-error text-h3">{{ error }}</span>
      </div>
      <v-virtual-scroll
          :items="taskStore.$state.tasks"
          class="w-100 h-auto"
          :key="tasksKey"
      >
        <template #default="{ item }">
          <v-card class="pa-3 mb-2" outlined :key="(item as Task).id">
             <v-row align="center" justify="space-between" no-gutters>
              <v-col cols="auto">
                <v-checkbox
                    :aria-label="`Mark ${(item as Task).title} as completed`"
                    v-model="getRef((item as Task).id).checked"
                    @change="toggleComplete(item)"

                />
              </v-col>

              <v-col>
                <div class="text-md-h5 text-h6">{{ (item as Task).title }}</div>
                <div class="text-md-body-1 text-body-2 text--secondary text-break">
                  {{ (item as Task).description }}
                </div>
                <div class="text-md-body-1 text-body-2 text--secondary">{{ (item as Task).prettyFulfilledDate }}</div>
              </v-col>

              <v-col cols="auto" class="d-flex flex-column gap-4 h-100">
                <v-btn icon aria-label="Edit task" @click="toggleUpdate((item as Task).id)">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn icon aria-label="Delete task" @click="deleteTask((item as Task).id)">
                  <v-icon color="red">mdi-delete</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </template>
      </v-virtual-scroll>
    </v-card>
  </div>
</template>
