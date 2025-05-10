
import {register, activateAcc, login} from "./endpoints.ts";
import type {UserCreate} from "@/models/UserCreate.ts";
import type {AuthForm} from "@/models/AuthForm.ts"

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
