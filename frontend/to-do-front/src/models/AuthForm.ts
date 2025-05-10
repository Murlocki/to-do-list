/**
 * @param {string} identifier - Идентификатор пользователя
 * @param {string} password - Пароль пользователя
 * @param {string} device - Устройство пользователя
 * @param {string} ip_address - Адрес устройства пользователя
 * @param {boolean} remember_me - Нужно ли запоминать сессиию пользователя
 */
export default class AuthForm{
    identifier: string
    password: string
    device: string = "unknown"
    ip_address: string = "unknown"
    remember_me: boolean = false

    /**
     * @param {string} identifier - Идентификатор пользователя
     * @param {string} password - Пароль пользователя
     * @param {string} device - Устройство пользователя
     * @param {string} ip_address - Адрес устройства пользователя
     * @param {boolean} remember_me - Нужно ли запоминать сессиию пользователя
     */
    constructor(identifier: string, password: string, device: string, ip_address: string, remember_me: boolean = false) {
        this.identifier = identifier
        this.password = password
        this.device = device
        this.ip_address = ip_address
        this.remember_me = remember_me
    }
}
