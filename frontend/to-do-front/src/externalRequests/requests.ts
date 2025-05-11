
import {register, activateAcc, login, logout, getForgotPasswordEmail, resetPassword, getMyTasks, updateTask} from "./endpoints.ts";
import type {UserCreate} from "@/models/UserCreate.ts";
import type {AuthForm} from "@/models/AuthForm.ts"
import type {TaskUpdate} from "@/models/TaskUpdate.ts"

export async function registerUser(user: UserCreate) {
    return await fetch(register, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(user)
    })
}
export async function activateAccount(token: string) {
    return await fetch(activateAcc, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
    })
}
export async function loginUser(authForm: AuthForm) {
    return await fetch(login, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(authForm)
    })
}
export async function loginOut(token: string) {
    return await fetch(logout, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
}
export async function getForgotEmail(email: string) {
    return await fetch(`${getForgotPasswordEmail}/${email}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
}
export async function updatePassword(token: string, password: string) {
    return await fetch(`${resetPassword}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({"new_password": password})
    })
}

export async function getAllTasks(token: string) {
    return await fetch(`${getMyTasks}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
}
export async function updateTaskById(taskId:number, newTask: TaskUpdate, token: string) {
    return await fetch(`${updateTask}/${taskId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newTask)
    })
}
