import {Status} from "@/models/Task.ts"
export default class TaskUpdate {
    title: string
    description: string | null = null
    status: Status = Status.IN_PROGRESS
    fulfilledDate: Date | null = null

    /**
     * Конструктор для создания/обновления задачи
     * @param {string} title
     * @param {string|null} description
     * @param {Status} status
     * @param {Date} fulfilledDate
     */
    constructor(title: string, description: string | null = null, status: Status = Status.IN_PROGRESS, fulfilledDate: Date|null = null) {
        this.title = title
        this.description = description
        this.status = status
        this.fulfilledDate = fulfilledDate
    }
}
