import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import { MainLayout } from './layouts/MainLayout';
import { HomePage } from './pages/HomePage';
import { DetectorPage } from './pages/DetectorPage';
import { PromptAnalyzerPage } from './pages/PromptAnalyzerPage';
import { DocumentScannerPage } from './pages/DocumentScannerPage';
import { DashboardPage } from './pages/DashboardPage';
import { AboutPage } from './pages/AboutPage';
import { LoginPage, RegisterPage } from './pages/AuthPages';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<HomePage />} />
              <Route path="detector" element={<DetectorPage />} />
              <Route path="prompts" element={<PromptAnalyzerPage />} />
              <Route path="documents" element={<DocumentScannerPage />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="about" element={<AboutPage />} />
              <Route path="login" element={<LoginPage />} />
              <Route path="register" element={<RegisterPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
