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

/**
 * Normalizes the API base URL to ensure proper endpoint routing.
 * Tolerates URLs with or without trailing slashes, and with or without '/api'.
 */
function getApiBaseUrl(): string {
  let url = (import.meta.env.VITE_API_URL || '').trim();
  if (!url) {
    return '/api';
  }
  // Strip trailing slashes
  url = url.replace(/\/+$/, '');
  
  // Ensure /api is appended if not already present
  if (!url.endsWith('/api') && !url.includes('/api/')) {
    url = `${url}/api`;
  }
  return url;
}

export const API_BASE_URL = getApiBaseUrl();

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds gives Render Free sufficient headroom to wake from sleep
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

/**
 * Extracts a diagnostic, user-friendly error message from failed API responses.
 */
export function extractErrorMessage(err: any): string {
  if (err?.response?.data?.detail) {
    return err.response.data.detail;
  }
  if (err?.code === 'ECONNABORTED' || err?.message?.includes('timeout')) {
    return 'Server cold start timeout. Render Free spins down during inactivity and requires ~30-45 seconds to wake up. Please wait a moment and try again.';
  }
  if (err?.response?.status === 503) {
    return 'Inference service is currently initializing. Please try again in a few seconds.';
  }
  if (err?.response?.status === 500) {
    return err?.response?.data?.detail || 'Internal server error while executing text classification.';
  }
  if (err?.response?.status === 404) {
    return `API endpoint not found (404). Ensure VITE_API_URL is configured to your Render backend root or /api. Target: ${API_BASE_URL}`;
  }
  if (!err?.response && (err?.message === 'Network Error' || !err?.status)) {
    return `Network Error: Unable to reach backend at ${API_BASE_URL}. The Render Free server may be asleep (waking up takes ~30-40s) or CORS is blocking the request.`;
  }
  return err?.message || 'Failed to perform inference. Ensure the backend server and model service are running.';
}

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

  // Model & System Health & Readiness APIs
  getModelInfo: async (): Promise<ModelInfoResponse> => {
    const response = await apiClient.get<ModelInfoResponse>('/model/info');
    return response.data;
  },

  getHealth: async (): Promise<{ status: string; timestamp: string; model_loaded: boolean }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  getReady: async (): Promise<{ status: string; ready: boolean; model_name: string }> => {
    const response = await apiClient.get('/ready');
    return response.data;
  },

  checkReady: async (): Promise<{ ready: boolean; status: string; detail?: string }> => {
    try {
      const response = await apiClient.get('/ready', { timeout: 10000 });
      return { ready: Boolean(response.data?.ready), status: response.data?.status || 'ready' };
    } catch (err: any) {
      if (err?.response?.status === 503) {
        return {
          ready: false,
          status: 'initializing',
          detail: err.response.data?.detail || 'Inference service is currently initializing. Please try again in a few seconds.',
        };
      }
      return { ready: false, status: 'unavailable', detail: extractErrorMessage(err) };
    }
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
