import {createRouter, createWebHistory} from 'vue-router'
import MainPage from "../components/MainPage/MainPage.vue";
import RegisterForm from "../components/Register/RegisterForm.vue";
import RegisterSubmittion from "../components/Register/RegisterSubmittion.vue";
import LoginPage from "../components/Login/LoginPage.vue";

const routes = [
    {
        path: '/',
        component: MainPage,
    },
    {
      path: '/login',component: LoginPage
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