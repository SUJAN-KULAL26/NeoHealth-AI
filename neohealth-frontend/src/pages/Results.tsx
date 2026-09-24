import React, { useState } from 'react';
import { PlusCircle, ArrowLeft, Printer, Share2, Check, CheckCircle2, History } from 'lucide-react';
import type { ScreeningResult } from '../types/screening';
import { ConfidenceCard } from '../components/ConfidenceCard';
import { GradCAMViewer } from '../components/GradCAMViewer';
import { ProbabilityChart } from '../components/ProbabilityChart';
import { RecommendationCard } from '../components/RecommendationCard';
import { Disclaimer } from '../components/Disclaimer';
import { formatDate } from '../utils/validation';

interface ResultsProps {
  result: ScreeningResult;
  onNewScreening: () => void;
  onNavigateHome: () => void;
  onViewHistory?: () => void;
  onBack?: () => void;
}

export const Results: React.FC<ResultsProps> = ({
  result,
  onNewScreening,
  onNavigateHome,
  onViewHistory,
  onBack,
}) => {
  const [copied, setCopied] = useState(false);

  const handlePrint = () => {
    window.print();
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ maxWidth: '1150px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2.25rem', paddingBottom: '4rem' }}>
      {/* Visual Workflow Stepper - All Completed */}
      <div className="workflow-stepper">
        <div className="stepper-item completed">
          <div className="stepper-circle"><CheckCircle2 size={16} /></div>
          <span>1. Input</span>
        </div>
        <div className="stepper-divider" />
        <div className="stepper-item completed">
          <div className="stepper-circle"><CheckCircle2 size={16} /></div>
          <span>2. Preview</span>
        </div>
        <div className="stepper-divider" />
        <div className="stepper-item completed">
          <div className="stepper-circle"><CheckCircle2 size={16} /></div>
          <span>3. Neural Inference</span>
        </div>
        <div className="stepper-divider" />
        <div className="stepper-item active">
          <div className="stepper-circle"><CheckCircle2 size={16} /></div>
          <span>4. Screening Report</span>
        </div>
      </div>

      {/* Top Header & Actions */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1.25rem',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
            <button
              onClick={onBack || onNavigateHome}
              className="btn-secondary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '0.45rem 0.9rem',
                fontSize: '0.84rem',
                fontWeight: 600,
                borderRadius: 'var(--radius-sm)',
              }}
            >
              <ArrowLeft size={15} /> Back
            </button>
            <span style={{ color: 'var(--text-subtle)' }}>•</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>Report Date: {formatDate(result.timestamp)}</span>
            <span style={{ color: 'var(--text-subtle)' }}>•</span>
            <span style={{
              fontSize: '0.78rem',
              color: '#34d399',
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              padding: '0.15rem 0.55rem',
              borderRadius: '999px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontWeight: 600,
            }}>
              <CheckCircle2 size={12} color="#10b981" /> Case Saved in History
            </span>
          </div>
          <h2 style={{ fontSize: '2rem', fontWeight: 800 }}>Infant Diagnostic Screening Report</h2>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
          {onViewHistory && (
            <button onClick={onViewHistory} className="btn-secondary" style={{ padding: '0.65rem 1.1rem', fontSize: '0.88rem' }}>
              <History size={16} /> View Case History
            </button>
          )}
          <button onClick={handleShare} className="btn-secondary" style={{ padding: '0.65rem 1.1rem', fontSize: '0.88rem' }}>
            {copied ? <Check size={16} color="#10b981" /> : <Share2 size={16} />}
            {copied ? 'Link Copied!' : 'Share Case'}
          </button>
          <button onClick={handlePrint} className="btn-secondary" style={{ padding: '0.65rem 1.1rem', fontSize: '0.88rem' }}>
            <Printer size={16} /> Print / Export PDF
          </button>
          <button onClick={onNewScreening} className="btn-primary" style={{ padding: '0.65rem 1.35rem', fontSize: '0.88rem' }}>
            <PlusCircle size={16} /> New Screening
          </button>
        </div>
      </div>

      {/* 1. Primary Diagnosis & Confidence Gauge */}
      <ConfidenceCard result={result} />

      {/* 2. Side-by-Side: Grad-CAM Explainability & Probability Distribution */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '2rem' }}>
        <GradCAMViewer gradCAM={result.gradCAM} />
        <ProbabilityChart probabilities={result.probabilities} />
      </div>

      {/* 3. Clinical Decision Support & Recommendations */}
      <RecommendationCard recommendations={result.recommendations} />

      {/* 4. Regulatory Medical Disclaimer */}
      <Disclaimer />

      {/* 5. Navigation Bar After Output Result Screen */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
        padding: '1.25rem 1.75rem',
        background: 'rgba(13, 21, 39, 0.75)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4)',
      }}>
        <button
          onClick={onBack || onNavigateHome}
          className="btn-secondary"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.55rem',
            padding: '0.75rem 1.4rem',
            fontSize: '0.95rem',
            fontWeight: 600,
          }}
        >
          <ArrowLeft size={18} /> Back
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
          {onViewHistory && (
            <button onClick={onViewHistory} className="btn-secondary" style={{ padding: '0.75rem 1.35rem', fontSize: '0.92rem' }}>
              <History size={16} /> View Case History
            </button>
          )}
          <button onClick={onNewScreening} className="btn-primary" style={{ padding: '0.75rem 1.5rem', fontSize: '0.92rem' }}>
            <PlusCircle size={17} /> Start New Screening
          </button>
        </div>
      </div>
    </div>
  );
};
