import axios from 'axios';
import {
  TextAnalysisResponse,
  PromptAnalysisResponse,
  DocumentAnalysisResponse,
  ModelInfoResponse,
  AuthResponse,
  User,
  AnalysisHistoryItem,
  UserStats,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000,
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('codewithanil_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const api = {
  // Detection APIs
  analyzeText: async (
    text: string,
    includeSentences: boolean = true,
    saveHistory: boolean = false
  ): Promise<TextAnalysisResponse> => {
    const response = await apiClient.post<TextAnalysisResponse>('/analyze/text', {
      text,
      include_sentences: includeSentences,
      save_history: saveHistory,
    });
    return response.data;
  },

  analyzePrompt: async (promptText: string): Promise<PromptAnalysisResponse> => {
    const response = await apiClient.post<PromptAnalysisResponse>('/analyze/prompt', {
      prompt: promptText,
    });
    return response.data;
  },

  analyzeDocument: async (
    file: File,
    saveHistory: boolean = true
  ): Promise<DocumentAnalysisResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('save_history', String(saveHistory));

    const response = await apiClient.post<DocumentAnalysisResponse>(
      '/analyze/document',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Model & System APIs
  getModelInfo: async (): Promise<ModelInfoResponse> => {
    const response = await apiClient.get<ModelInfoResponse>('/model/info');
    return response.data;
  },

  getHealth: async (): Promise<{ status: string; timestamp: string; model_loaded: boolean }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // History & Reports
  getAnalysisHistory: async (): Promise<AnalysisHistoryItem[]> => {
    const response = await apiClient.get<AnalysisHistoryItem[]>('/analysis/history');
    return response.data;
  },

  getAnalysisById: async (id: number): Promise<TextAnalysisResponse> => {
    const response = await apiClient.get<TextAnalysisResponse>(`/analysis/${id}`);
    return response.data;
  },

  deleteAnalysis: async (id: number): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.delete(`/analysis/${id}`);
    return response.data;
  },

  getUserStats: async (): Promise<UserStats> => {
    const response = await apiClient.get<UserStats>('/analysis/stats');
    return response.data;
  },

  downloadReportPdf: async (id: number): Promise<Blob> => {
    const response = await apiClient.get(`/reports/${id}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Auth APIs
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  register: async (name: string, email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', {
      name,
      email,
      password,
    });
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // Continue client cleanup even if network fails
    }
  },
};
