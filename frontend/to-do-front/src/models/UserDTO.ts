/**
 * Класс для передачи данных от бэка к фронту о пользователях
 * @param {number} id - user id from db
 * @param {string} email - User email
 * @param {string} firstName - User first name
 * @param {string} lastName - User last name
 * @param {string} userName - User user name
 * */
export class UserDTO {
    id: number;
    email: string;
    firstName: string;
    lastName: string;
    username: string;

    /**
     * Конструктор класса
     * @param {number} id - user id from db
     * @param {string} email - User email
     * @param {string} firstName - User first name
     * @param {string} lastName - User last name
     * @param {string} userName - User user name
     * */
    constructor(id:number, email: string, firstName: string, lastName: string, userName: string) {
        this.email = email
        this.firstName = firstName
        this.lastName = lastName
        this.username = userName
        this.id = id;
    }

}
