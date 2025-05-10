export const userNameRegex: RegExp = new RegExp('^[A-Za-z][A-Za-z0-9_]{2,}$', 'i');
export const nameRegex: RegExp = new RegExp('^[A-Z][a-z]+(-[A-Z][a-z]+)*$')
export const passwordRegex: RegExp = new RegExp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[!@#$%^&*=])[A-Za-z\\d!@#$%^&*=]{8,}$')
export const emailRegex: RegExp = new RegExp('^[A-Za-z][A-Za-z0-9_]*@[a-z]+\\.[a-z]+$', 'i');