/**
 * Класс для передачи данных от бэка к фронту о пользователях
 * @param {number} id - user id from db
 * @param {string} email - User email
 * @param {string} firstName - User first name
 * @param {string} lastName - User last name
 * @param {string} userName - User user name
 * @param {string} password - User password
 * @param {boolean} isActive - User is active
 * @param {boolean} isSuperuser - Is user a admin
 * */
export class UserCreate {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    username: string;
    password: string;
    isActive: boolean;
    isSuperuser: boolean;

    /**
     * Конструктор класса
     * @param {number} id - user id from db
     * @param {string} email - User email
     * @param {string} firstName - User first name
     * @param {string} lastName - User last name
     * @param {string} userName - User user name
     * @param {string} password - User password
     * @param {boolean} isActive - User is active
     * @param {boolean} isSuperuser - Is user a admin
     * */
    constructor(id:number, email: string, firstName: string, lastName: string, userName: string, password:string, isActive:boolean, isSuperuser:boolean) {
        this.email = email
        this.first_name = firstName
        this.last_name = lastName
        this.username = userName
        this.password = password
        this.id = id;
        this.isActive = isActive;
        this.isSuperuser = isSuperuser
    }
}
