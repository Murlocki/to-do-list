import { defineStore } from 'pinia'
import Cookies from 'js-cookie'

const tokenCookieKey = 'toDoListToken'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: Cookies.get(tokenCookieKey) || '',
    }),
    getters: {
        isLoggedIn: (state) => !!state.token,
    },
    actions: {
        setToken(token: string) {
            Cookies.set(tokenCookieKey, token)
            this.token = token
        },
        clearToken() {
            Cookies.remove(tokenCookieKey)
            this.token = ''
        },
        refreshTokenFromCookie() {
            this.token = Cookies.get(tokenCookieKey) || ''
        }
    }
})