import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { User, Todo, TodoCreate, TodoUpdate } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      withCredentials: true,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Auth endpoints
  async getGoogleAuthUrl(): Promise<string> {
    // This method will redirect to Google OAuth, so we return the URL directly
    return `${API_URL}/api/v1/auth/google/login`;
  }

  async handleAuthCallback(code: string): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get(
      `/api/v1/auth/google/callback?code=${code}`
    );
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  async logout(): Promise<{ message: string }> {
    const response = await this.client.post('/api/v1/auth/logout');
    return response.data;
  }

  // Todo endpoints
  async getTodos(): Promise<Todo[]> {
    const response: AxiosResponse<Todo[]> = await this.client.get('/api/v1/todos');
    return response.data;
  }

  async getTodo(id: string): Promise<Todo> {
    const response: AxiosResponse<Todo> = await this.client.get(`/api/v1/todos/${id}`);
    return response.data;
  }

  async createTodo(todo: TodoCreate): Promise<Todo> {
    const response: AxiosResponse<Todo> = await this.client.post('/api/v1/todos', todo);
    return response.data;
  }

  async updateTodo(id: string, todo: TodoUpdate): Promise<Todo> {
    const response: AxiosResponse<Todo> = await this.client.put(`/api/v1/todos/${id}`, todo);
    return response.data;
  }

  async deleteTodo(id: string): Promise<{ message: string }> {
    const response = await this.client.delete(`/api/v1/todos/${id}`);
    return response.data;
  }
}

export const apiService = new ApiService();