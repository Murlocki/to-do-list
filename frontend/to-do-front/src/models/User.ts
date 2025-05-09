export default class UserDTO {
    id: number
    email: string
    firstName: string
    lastName: string
    userName: string

    constructor(id: number=0, email: string="", firstName: string="", lastName: string="", userName: string="ffefefefe") {
        this.id = id
        this.email = email
        this.firstName = firstName
        this.lastName = lastName
        this.userName = userName
    }
}

