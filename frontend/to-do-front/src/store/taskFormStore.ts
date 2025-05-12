import {defineStore} from "pinia";
import {Status} from "@/models/Task.ts";
export const useTaskFormStore = defineStore("taskForm", {
    state: ()=>({
        isOpen: false,
        title:"" as string,
        description: null,
        fulfilledDate: null,
        time:null,
        status: Status.IN_PROGRESS,
    }),
    getters:{
       isDatePresent(state){
           return state.fulfilledDate == null;
       },
       fullDate(state){
           if(state.fulfilledDate == null){
               return null
           }
           if(state.time == null){
               return new Date(state.fulfilledDate)
           }

           const dateObject = new Date(state.fulfilledDate)
           const [hours, minutes] = (state.time as String).split(':').map(Number);
           dateObject.setHours(hours);
           dateObject.setMinutes(minutes);
           dateObject.setSeconds(0);
           dateObject.setMilliseconds(0);
           return dateObject;
       }
    },
    actions: {
        async setIsOpen(isOpen: boolean) {
            this.$state.isOpen = isOpen;
            console.log(isOpen);
        }
    }
})