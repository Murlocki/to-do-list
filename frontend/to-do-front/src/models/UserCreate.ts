/**
 * @param {string} email - User email
 * @param {string} firstName - User first name
 * @param {string} lastName - User last name
 * @param {string} userName - User user name
 * @param {string} password - User password
 * */
export class UserCreate {
    email: string
    firstName: string
    lastName: string
    userName: string
    password: string

    /**
     * @param {string} email - User email
     * @param {string} firstName - User first name
     * @param {string} lastName - User last name
     * @param {string} userName - User user name
     * @param {string} password - User password
     * */
    constructor(email: string, firstName: string, lastName: string, userName: string, password:string) {
        this.email = email
        this.firstName = firstName
        this.lastName = lastName
        this.userName = userName
        this.password = password
    }
}

