const apiUrl = import.meta.env.VITE_API_URL;

// EndPoints
export const register = `${apiUrl}/auth/register`;
export const activateAcc = `${apiUrl}/auth/activate_account`;
export const login = `${apiUrl}/auth/login`;
export const logout = `${apiUrl}/auth/logout`;
export const getForgotPasswordEmail = `${apiUrl}/auth/get_forgot_password_email`
export const resetPassword = `${apiUrl}/auth/forgot_password`
export const getMyTasks = `${apiUrl}/task/me`
export const updateTask = `${apiUrl}/task/me`
export const createTask = `${apiUrl}/task/me`
export const deleteTask = `${apiUrl}/task/me`

