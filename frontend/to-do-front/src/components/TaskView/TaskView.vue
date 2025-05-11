<script setup lang="ts">
import {onMounted, ref, reactive} from "vue";
import {useAuthStore} from "@/store/authStore.ts";
import {getAllTasks, updateTaskById} from "@/externalRequests/requests.ts";
import {useRouter} from "vue-router";
import {useTaskStore} from "@/store/taskStore.ts";
import Task from "@/models/Task.ts";
import TaskUpdate from "@/models/TaskUpdate.ts";
import {Status} from "@/models/Task.ts"


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

  taskStore.$state.tasks.forEach((item: Task) => {
    scrollerRefs.set(item.id, {
      checked: item.status === Status.COMPLETED,
      loading: false,
    })
  })
  console.log(scrollerRefs)
  console.log(scrollerRefs.get(1)?.checked)
  loading.value = false;
})

type ScrollerRef = {
  checked: boolean
  loading: boolean
}

const scrollerRefs = reactive(new Map<number, ScrollerRef>());
function getRef(taskId: number) {
  return scrollerRefs.get(taskId) ?? { checked: false, loading: false };
}
const error = ref('');

async function toggleComplete(task: Task) {
  const refItem = scrollerRefs.get(task.id);
  if (!refItem) return;

  refItem.loading = true;

  try {
    const taskUpdate = new TaskUpdate(
        task.title,
        task.description,
        refItem.checked ? Status.COMPLETED : Status.IN_PROGRESS,
        task.fulfilledDate
    );
    const response = await updateTaskById(task.id, taskUpdate, authStore.token);
    const response_json = await response.json();

    if (response.ok) {
      await authStore.setToken(response_json.token);
      error.value = "";
      await taskStore.updateTaskById(task.id, taskUpdate);
    } else if (response.status === 401 || response.status === 403) {
      authStore.clearToken();
      await router.push("/");
    } else {
      authStore.setToken(response_json.detail?.token);
      error.value = response_json.detail?.error || "Unknown error";
    }
  } catch (e) {
    console.error("Ошибка при обновлении задачи:", e);
    error.value = "Ошибка сети или сервера";
  } finally {
    refItem.loading = false;
  }
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
            aria-label="Add new task"
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
          :loading="loading"
      >
        <template #default="{ item }">
          <v-card class="pa-3 mb-2" outlined>
            <v-progress-linear v-if="getRef((item as Task).id).loading" height="40" indeterminate></v-progress-linear>
            <v-row align="center" justify="space-between" no-gutters v-if="!getRef((item as Task).id).loading">
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
                  FFPFPEPFEPFPFPEFPEPFEPFPEPEFPFPFPEPFPFP
                </div>
                <div class="text-md-body-1 text-body-2 text--secondary">{{ (item as Task).prettyFulfilledDate }}</div>
              </v-col>

              <v-col cols="auto" class="d-flex flex-column gap-4 h-100">
                <v-btn icon  aria-label="Edit task">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn icon aria-label="Delete task">
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
