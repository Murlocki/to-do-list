import {defineStore} from 'pinia'
import Task from "@/models/Task.ts"
import TaskUpdate from "@/models/TaskUpdate.ts"

export const useTaskStore = defineStore('task', {
    state: () => ({
        tasks: [] as Task[],
    }),
    getters: {},
    actions: {
        async fetchTasks(tasks: Task[]) {
            console.log(tasks)
            if (tasks && tasks.length > 0) {
                tasks.forEach((task: Task): void => {
                    this.$state.tasks.push(new Task(
                        task.id,task.title,task.description,task.status,task.userId,task.fulfilledDate
                    ))
                })
            }
            console.log(this.$state.tasks)
        },
        async updateTaskById(id: string, task: TaskUpdate) {
            const oldTask = await this.$state.tasks.find((task: Task) => task.id === id) as Task;
            await oldTask.updateByTask(task)
            console.log(oldTask)
        }
    }
})