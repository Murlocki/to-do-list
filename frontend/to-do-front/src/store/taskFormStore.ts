import {defineStore} from "pinia";
import {Status} from "@/models/Task.ts";
import Task from "@/models/Task.ts";
export const useTaskFormStore = defineStore("taskForm", {
    state: ()=>({
        isUpdating: false,
        isOpen: false,
        id: null,
        title:"" as string,
        description: null,
        fulfilledDate: null,
        time:null,
        status: Status.IN_PROGRESS,
        version: null,
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
        },
        async setTask(task:Task){
            this.isUpdating = true;
            this.$state.id = task.id;
            this.$state.title = task.title;
            this.$state.description = task.description;
            if (task.fulfilledDate != null){
                this.$state.fulfilledDate = task.fulfilledDate.toISOString().slice(0,10);
                this.$state.time = task.fulfilledDate.toTimeString().slice(0,8);
            }
            this.$state.status = task.status;
            this.$state.version = task.version;
        }
    }
})