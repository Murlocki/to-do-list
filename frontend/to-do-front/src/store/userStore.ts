import { defineStore } from 'pinia'
import UserDTO from "../models/User.ts";


export const useUserStore = defineStore('user', {
    state: () => ({
        user: new UserDTO(),
    }),
    getters: {

    },
    actions: {

    }
})