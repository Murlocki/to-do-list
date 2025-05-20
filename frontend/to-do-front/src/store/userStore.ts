import {defineStore} from 'pinia'
import {UserDTO} from "@/models/UserDTO.ts";

type State = {
    user: UserDTO | null,
}

export const useUserStore = defineStore('user', {
    state: (): State => ({
        user: null,
    }),
    getters: {},
    actions: {
        setUser(user: UserDTO) {
            this.$state.user = user;
        },

    }
})