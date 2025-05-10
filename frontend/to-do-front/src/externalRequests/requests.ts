
import {register} from "./endpoints.ts";
import type {UserCreate} from "@/models/UserCreate.ts";

export async function registerUser(user: UserCreate) {
    return await fetch(register, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(user)
    })
}