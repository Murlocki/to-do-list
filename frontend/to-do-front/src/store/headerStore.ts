import {defineStore} from 'pinia'

export const useHeaderStore = defineStore('headerStore', {
    state: () => ({
        menuIsOpen: false,
    }),
    actions:{
        async changeMenuStatus(menuState: boolean){
            this.$state.menuIsOpen = menuState
            console.log(menuState)
        },
    },
})