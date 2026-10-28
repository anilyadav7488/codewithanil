import React, { useState, useRef } from 'react';
import { 
  FileSearch, 
  Upload, 
  FileText, 
  Download, 
  AlertCircle, 
  CheckCircle2, 
  Trash2, 
  ShieldCheck,
  FileWarning
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentAnalysisResponse } from '../types';
import { ScoreGauge } from '../components/ScoreGauge';
import { SentenceHighlighter } from '../components/SentenceHighlighter';

export const DocumentScannerPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<DocumentAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDownloadingReport, setIsDownloadingReport] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const supportedFormats = ['.pdf', '.docx', '.txt'];
  const maxSizeBytes = 15 * 1024 * 1024; // 15MB

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    setResult(null);

    const ext = '.' + selectedFile.name.split('.').pop()?.toLowerCase();
    if (!supportedFormats.includes(ext)) {
      setError(`Unsupported file format "${ext}". Please upload a PDF, DOCX, or TXT file.`);
      return;
    }

    if (selectedFile.size > maxSizeBytes) {
      setError('File size exceeds the 15MB limit. Please upload a smaller document.');
      return;
    }

    setFile(selectedFile);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleScanDocument = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await api.analyzeDocument(file, true);
      setResult(data);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          'Failed to process document. Ensure the file contains parseable text.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!result?.analysis?.id) return;
    setIsDownloadingReport(true);
    try {
      const blob = await api.downloadReportPdf(result.analysis.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `codewithanil-report-${result.analysis.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to download PDF audit report.');
    } finally {
      setIsDownloadingReport(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Title */}
      <div className="text-center max-w-3xl mx-auto space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-xs font-semibold text-teal-400">
          <FileSearch className="w-4 h-4" /> Multi-Format Document Ingestion
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Document Scanner
        </h1>
        <p className="text-sm text-slate-400">
          Upload PDF, DOCX, or TXT manuscripts. Extract content safely without macro execution and generate downloadable PDF audit certificates.
        </p>
      </div>

      {/* Upload Box */}
      <div className="rounded-2xl bg-navy-900/60 backdrop-blur-xl border border-slate-800 shadow-2xl p-6 sm:p-8 space-y-6">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center ${
            isDragging
              ? 'border-electric-400 bg-electric-500/10 scale-[1.01]'
              : 'border-slate-800 hover:border-slate-700 bg-navy-950/60'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt"
            className="hidden"
          />

          <div className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center mb-4">
            <Upload className="w-8 h-8" />
          </div>

          <h3 className="text-base font-bold text-white mb-1">
            {file ? file.name : 'Choose a file or drag & drop it here'}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mb-3">
            Supports PDF, DOCX, or plain TXT up to 15MB. Macros and active scripts are strictly ignored.
          </p>

          <span className="px-3.5 py-1.5 rounded-lg bg-slate-800 text-xs font-medium text-slate-200 hover:bg-slate-700 transition-colors">
            {file ? 'Replace File' : 'Browse Files'}
          </span>
        </div>

        {/* Selected file preview bar */}
        {file && (
          <div className="flex items-center justify-between p-4 rounded-xl bg-navy-950 border border-slate-800 text-xs">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-teal-400" />
              <div>
                <span className="font-semibold text-slate-200 block">{file.name}</span>
                <span className="text-slate-500">
                  {(file.size / 1024).toFixed(1)} KB • {file.name.split('.').pop()?.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                  setResult(null);
                }}
                className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                title="Remove file"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={handleScanDocument}
                disabled={isLoading}
                className="px-5 py-2 rounded-lg bg-teal-500 hover:bg-teal-400 text-navy-950 font-bold flex items-center gap-2 shadow-md shadow-teal-500/20 disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-navy-950 border-t-transparent rounded-full animate-spin" />
                    <span>Extracting & Analyzing...</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    <span>Scan Document</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Error notification */}
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-start gap-3">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <div>
              <strong>Scanner Alert: </strong>
              {error}
            </div>
          </div>
        )}
      </div>

      {/* Results View */}
      {result && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Header Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 p-6 rounded-2xl bg-navy-900/60 border border-slate-800">
            <div>
              <span className="text-xs text-teal-400 uppercase tracking-wider font-semibold">
                Scan Completed Successfully
              </span>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                {result.filename}
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Extracted {result.extracted_word_count} words from file structure.
              </p>
            </div>

            {result.analysis?.id && (
              <button
                onClick={handleDownloadPdf}
                disabled={isDownloadingReport}
                className="px-4 py-2.5 rounded-xl bg-electric-500/10 border border-electric-500/30 hover:bg-electric-500/20 text-electric-400 text-xs font-bold flex items-center gap-2 transition-colors"
              >
                {isDownloadingReport ? (
                  <div className="w-3.5 h-3.5 border-2 border-electric-400 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                <span>Download PDF Audit Report</span>
              </button>
            )}
          </div>

          {/* Scanned PDF OCR Notice if detected */}
          {result.requires_ocr_warning && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-3">
              <FileWarning className="w-5 h-5 text-amber-400 shrink-0" />
              <div>
                <strong>Low Text Density / Scanned PDF Notice: </strong>
                Very few text characters were extracted from this document. If this is an image-based scanned document, an Optical Character Recognition (OCR) pre-processing step is required before transformer tokenization.
              </div>
            </div>
          )}

          {/* Primary Model Score Gauge */}
          <ScoreGauge
            aiScore={result.analysis.ai_score}
            humanScore={result.analysis.human_score}
            prediction={result.analysis.prediction}
            isInconclusive={result.analysis.is_inconclusive}
            confidenceLevel={result.analysis.confidence_level}
            processingTimeMs={result.analysis.processing_time_ms}
            wordCount={result.analysis.word_count}
          />

          {/* Document Text Preview */}
          <div className="rounded-2xl bg-navy-900/40 border border-slate-800 p-6 space-y-3">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Extracted Text Preview
            </h4>
            <div className="p-4 rounded-xl bg-navy-950 border border-slate-800 text-xs text-slate-300 max-h-48 overflow-y-auto font-mono whitespace-pre-wrap leading-relaxed">
              {result.text_preview}
            </div>
          </div>

          {/* Sentence Highlighting if present */}
          {result.analysis.sentence_analyses && (
            <SentenceHighlighter
              sentences={result.analysis.sentence_analyses}
              originalText={result.analysis.input_text}
            />
          )}
        </div>
      )}
    </div>
  );
};
