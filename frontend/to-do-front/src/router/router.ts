import { createMemoryHistory, createRouter } from 'vue-router'
import MainPage from "../components/MainPage/MainPage.vue";

const routes = [
    {
        path: '/',
        component: MainPage,
    }
]
export const router = createRouter({
    history: createMemoryHistory(),
    routes,
})