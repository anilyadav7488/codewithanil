export type DetectionLabel = 'Human' | 'AI-Generated' | 'Inconclusive';

export interface SentenceAnalysis {
  sentence_index: number;
  text: string;
  ai_score: number;
  human_score: number;
  prediction: string;
  is_highlighted: boolean;
  confidence_rating: 'Low' | 'Moderate' | 'High';
}

export interface TextAnalysisResponse {
  id?: number;
  input_text: string;
  word_count: number;
  character_count: number;
  prediction: DetectionLabel;
  ai_score: number; // calibrated 0.0 - 1.0
  human_score: number; // calibrated 0.0 - 1.0
  raw_logits?: {
    human_logit: number;
    ai_logit: number;
  };
  is_inconclusive: boolean;
  confidence_level: 'Low' | 'Medium' | 'High';
  model_name: string;
  model_version: string;
  processing_time_ms: number;
  limitations: string[];
  sentence_analyses?: SentenceAnalysis[];
  created_at?: string;
}

export interface PromptAnalysisResponse {
  original_prompt: string;
  overall_score: number; // 0 - 100
  metrics: {
    clarity: number; // 0 - 100
    specificity: number; // 0 - 100
    context: number; // 0 - 100
    constraints: number; // 0 - 100
    output_formatting: number; // 0 - 100
    completeness: number; // 0 - 100
    ambiguity_reduction: number; // 0 - 100 (higher means less ambiguous)
  };
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  improved_prompt: string;
  analysis_summary: string;
  disclaimer: string;
}

export interface DocumentAnalysisResponse {
  document_id: number;
  filename: string;
  file_type: string;
  extracted_word_count: number;
  text_preview: string;
  requires_ocr_warning: boolean;
  analysis: TextAnalysisResponse;
}

export interface ModelInfoResponse {
  model_name: string;
  architecture: string;
  framework: string;
  intended_use: string;
  training_dataset: string;
  license: string;
  cpu_compatible: boolean;
  supported_languages: string[];
  decision_thresholds: {
    inconclusive_lower: number;
    inconclusive_upper: number;
  };
  known_limitations: string[];
  disclaimer: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface AnalysisHistoryItem {
  id: number;
  user_id?: number;
  analysis_type: string;
  prediction: string;
  model_score: number;
  model_version: string;
  word_count: number;
  snippet: string;
  created_at: string;
  has_report: boolean;
}

export interface UserStats {
  total_analyses: number;
  ai_count: number;
  human_count: number;
  inconclusive_count: number;
  average_ai_score: number;
  total_words_analyzed: number;
}
