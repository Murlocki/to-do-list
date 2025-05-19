import {createRouter, createWebHistory} from 'vue-router'
import MainPage from "@/components/MainPage/MainPage.vue";
import RegisterForm from "@/components/Register/RegisterForm.vue";
import RegisterSubmittion from "@/components/Register/RegisterSubmittion.vue";
import LoginPage from "@/components/Login/LoginPage.vue";
import ResetEmailForm from "@/components/RestorePassword/ResetEmailForm.vue";
import ChangePasswordForm from "@/components/RestorePassword/ChangePasswordForm.vue";
import TaskView from "@/components/TaskView/TaskView.vue";
import ProfileView from "@/components/ProfileView/ProfileView.vue";

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
    },
    {
        path: '/login/forgot-password',
        component: ResetEmailForm
    },
    {
        path:'/login/forgot-password/:token',
        component: ChangePasswordForm,
        props: true,
    },
    {
        path:'/tasks',
        component: TaskView
    },
    {
        path:'/profile',
        component: ProfileView
    }
]
export const router = createRouter({
    history: createWebHistory(),
    routes,
})