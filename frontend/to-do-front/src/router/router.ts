import {createRouter, createWebHistory} from 'vue-router'
import MainPage from "../components/MainPage/MainPage.vue";
import RegisterForm from "../components/Register/RegisterForm.vue";
import RegisterSubmittion from "../components/Register/RegisterSubmittion.vue";

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
    },
    {
        path:'/register/submit/:token',
        component: RegisterSubmittion,
        props: true
    }
]
export const router = createRouter({
    history: createWebHistory(),
    routes,
})