import axios from './axios';

interface LoginResponse {
    token: string;
    // add other user info fields if any
}

export async function loginUser(username: string, password: string): Promise<LoginResponse> {
    const response = await axios.post('/user/login/', { username, password }); // your Django endpoint
    return response.data;
}
