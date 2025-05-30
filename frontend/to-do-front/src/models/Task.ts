import type TaskUpdate from "@/models/TaskUpdate.ts";

export const Status = {
    IN_PROGRESS: 0,
    COMPLETED: 1,
} as const;

type Status = typeof Status[keyof typeof Status];
export const StatusLabels: Record<Status, string> = {
    [Status.IN_PROGRESS]: "In Progress",
    [Status.COMPLETED]: "Completed",
};

/**
 * Класс для получения данных о задачах
 * @param {number} id - task id from bd
 * @param {string} title - task title
 * @param {string|null} description - task description
 * @param {Status} status - task status
 * @param {number} userId - task user id
 * @param {Date|null} fulfilledDate - task fulfilled date
 * */
export default class Task {
    _id: number
    _title: string
    _description: string | null = null
    _status: Status = Status.IN_PROGRESS
    _userId: number
    _fulfilledDate: Date|null = null
    _version: number = 0
    /**
     * Класс для получения данных о задачах
     * @param {number} id - task id from bd
     * @param {string} title - task title
     * @param {string|null} description - task description
     * @param {Status} status - task status
     * @param {number} userId - task user id
     * @param {Date|null} fulfilledDate - task fulfilled date
     * @param {int} version
     * */
    constructor(id:number, title:string, description:string|null,status:Status,userId:number,fulfilledDate:string|null=null ,version:number = 0) {
        this._id = id
        this._title = title
        this._description = description
        this._status = status
        this._userId = userId
        this._fulfilledDate = fulfilledDate? new Date(fulfilledDate): null
        this._version = version
    }
    public get title(): string {
        return this._title
    }
    public get id(): number {
        return this._id
    }
    public get description(): string|null {
        return this._description
    }
    public get status(): Status {
        return this._status
    }
    public get userId(): number {
        return this._userId
    }
    public get fulfilledDate(): Date|null {
        return this._fulfilledDate
    }
    public get statusName(): string {
        return StatusLabels[this._status]
    }
    public get version(): number {
        return this._version
    }
    public get prettyFulfilledDate():string|null {
        if (this.fulfilledDate instanceof Date) {
            return this.fulfilledDate.toLocaleString('en-EN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            });
        }
        return null;
    }
    public set status(value: Status) {
        this._status = value;
    }
    /**
     * Update task by taskUpdate
     * @param {TaskUpdate} task
     */
    public updateByTask(task: TaskUpdate) {
        this._status = task.status;
        this._description = task.description;
        this._title = task.title;
        this._fulfilledDate = task.fulfilledDate
        this._version = task.version
    }
}