import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import { VTimePicker } from 'vuetify/labs/VTimePicker'
import {createPinia} from "pinia";
import {router} from "./router/router.ts";
const vuetify = createVuetify({
    components: {
        ...components,
        VTimePicker, // добавляем сюда
    },
    directives,
    icons: {
        defaultSet: 'mdi',
    },
    theme: {
        defaultTheme: 'light',
    },
})


const pinia = createPinia()


createApp(App).use(vuetify).use(pinia).use(router).mount('#app')
