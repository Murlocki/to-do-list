import {createRouter, createWebHistory} from 'vue-router'
import MainPage from "../components/MainPage/MainPage.vue";
import RegisterForm from "../components/Register/RegisterForm.vue";

const routes = [
    {
        path: '/',
        component: MainPage,
    },
    {
      path: '/login',component: MainPage
    },
    {
        path: '/register',
        component: RegisterForm
    }
]
export const router = createRouter({
    history: createWebHistory(),
    routes,
})