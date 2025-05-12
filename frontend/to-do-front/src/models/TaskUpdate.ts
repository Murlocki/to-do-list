import {Status} from "@/models/Task.ts"
export default class TaskUpdate {
    title: string
    description: string | null = null
    status: Status = Status.IN_PROGRESS
    fulfilledDate: Date | null = null
    version: number = 0
    /**
     * Конструктор для создания/обновления задачи
     * @param {string} title
     * @param {string|null} description
     * @param {Status} status
     * @param {Date} fulfilledDate
     * @param {number} version
     */
    constructor(title: string, description: string | null = null, status: Status = Status.IN_PROGRESS, fulfilledDate: Date|null = null, version: number = 0) {
        this.title = title
        this.description = description
        this.status = status
        this.fulfilledDate = fulfilledDate
        this.version = version
    }
}
