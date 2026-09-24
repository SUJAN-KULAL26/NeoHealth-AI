import { useState, useCallback, useEffect } from 'react';
import type {
  ScreeningInput,
  ScreeningResult,
  ScreeningStatus,
  ScreeningHistoryItem,
  DiseaseClass,
} from '../types/screening';
import { analyzeImage, getHistory, deleteFromHistory, clearHistory } from '../services/api';
import { validateImageFile } from '../utils/validation';

export type PageName = 'home' | 'screening' | 'processing' | 'results' | 'uncertain' | 'history';

export function useScreening() {
  const [activePage, setActivePage] = useState<PageName>('home');
  const [previousPage, setPreviousPage] = useState<PageName>('screening');
  const [input, setInput] = useState<ScreeningInput | null>(null);
  const [status, setStatus] = useState<ScreeningStatus>('idle');
  const [result, setResult] = useState<ScreeningResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processingStep, setProcessingStep] = useState<number>(0);
  const [processingLabel, setProcessingLabel] = useState<string>('');
  const [progress, setProgress] = useState<number>(0);
  const [history, setHistory] = useState<ScreeningHistoryItem[]>([]);

  const navigateTo = useCallback((page: PageName) => {
    setActivePage((curr) => {
      if (curr !== page) {
        setPreviousPage(curr);
      }
      return page;
    });
  }, []);

  const goBack = useCallback(() => {
    setActivePage((curr) => {
      if (curr === 'results' || curr === 'uncertain') {
        return previousPage === 'results' || previousPage === 'uncertain' ? 'screening' : previousPage;
      }
      return previousPage || 'home';
    });
  }, [previousPage]);

  // Load history on mount
  useEffect(() => {
    setHistory(getHistory());
  }, []);

  const refreshHistory = useCallback(() => {
    setHistory(getHistory());
  }, []);

  /**
   * Sets image input from upload, webcam capture, or curated sample preset
   */
  const setImageInput = useCallback(
    (
      imageSrc: string,
      source: 'upload' | 'webcam' | 'preset' = 'upload',
      bodySite: string = 'Face / Cheeks',
      patientNotes: string = '',
      file?: File,
      presetCondition?: DiseaseClass
    ) => {
      setError(null);

      if (file) {
        const validation = validateImageFile(file);
        if (!validation.isValid) {
          setError(validation.error || 'Invalid image file.');
          return false;
        }
      }

      setInput({
        file,
        imageSrc,
        source,
        presetCondition,
        bodySite,
        patientNotes,
        timestamp: new Date().toISOString(),
      });

      setStatus('input');
      return true;
    },
    []
  );

  /**
   * Starts the multi-stage AI diagnostic screening process
   */
  const startAnalysis = useCallback(async (overrideBodySite?: string, overrideNotes?: string) => {
    if (!input) {
      setError('Please select or capture a valid medical image before starting analysis.');
      return;
    }

    const currentInput: ScreeningInput = {
      ...input,
      bodySite: overrideBodySite || input.bodySite,
      patientNotes: overrideNotes !== undefined ? overrideNotes : input.patientNotes,
    };

    setError(null);
    setStatus('processing');
    setActivePage('processing');
    setProgress(0);
    setProcessingStep(1);

    try {
      const screeningResult = await analyzeImage(currentInput, (step, label) => {
        setProcessingStep(step);
        setProcessingLabel(label);
        setProgress(Math.round((step / 5) * 100));
      });

      setResult(screeningResult);
      refreshHistory();

      if (screeningResult.isUncertain) {
        setStatus('uncertain');
        setActivePage('uncertain');
      } else {
        setStatus('results');
        setActivePage('results');
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'An unexpected error occurred during AI processing.';
      setError(msg);
      setStatus('error');
      setActivePage('screening');
    }
  }, [input, refreshHistory]);

  /**
   * Resets screening state for a new scan
   */
  const resetScreening = useCallback(() => {
    setInput(null);
    setResult(null);
    setError(null);
    setStatus('idle');
    setProgress(0);
    setProcessingStep(0);
    setProcessingLabel('');
    setActivePage('screening');
  }, []);

  /**
   * Loads a historic screening record directly into the results view
   */
  const loadHistoryItem = useCallback((item: ScreeningHistoryItem) => {
    setPreviousPage('history');
    setResult(item.result);
    setInput({
      imageSrc: item.imageSrc,
      source: 'upload',
      bodySite: item.bodySite,
      timestamp: item.date,
    });
    if (item.result.isUncertain) {
      setStatus('uncertain');
      setActivePage('uncertain');
    } else {
      setStatus('results');
      setActivePage('results');
    }
  }, []);

  /**
   * Removes item from history
   */
  const removeHistoryItem = useCallback(
    (id: string) => {
      deleteFromHistory(id);
      refreshHistory();
    },
    [refreshHistory]
  );

  /**
   * Clears all history
   */
  const clearAllHistory = useCallback(() => {
    clearHistory();
    refreshHistory();
  }, [refreshHistory]);

  return {
    activePage,
    setActivePage,
    previousPage,
    navigateTo,
    goBack,
    input,
    status,
    result,
    error,
    setError,
    processingStep,
    processingLabel,
    progress,
    history,
    setImageInput,
    startAnalysis,
    resetScreening,
    loadHistoryItem,
    removeHistoryItem,
    clearAllHistory,
  };
}
