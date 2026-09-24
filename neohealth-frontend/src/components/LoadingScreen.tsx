import React from 'react';
import { Cpu, CheckCircle2, Loader2, Sparkles, Activity } from 'lucide-react';

interface LoadingScreenProps {
  progress: number;
  currentStep: number;
  stepLabel: string;
  onCancel?: () => void;
}

const PEDIATRIC_DL_STEPS = [
  'Image Normalization & Pediatric Color Balance',
  'Deep Convolutional Feature Map Extraction (Layer 4 Activation)',
  '6-Class Infant Neural Network Ensemble Inference',
  'Grad-CAM Spatial Gradient Heatmap Computation',
  'Pediatric Decision Support & Care Synthesis',
];

export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  progress,
  currentStep,
  stepLabel,
  onCancel,
}) => {
  return (
    <div className="glass-panel" style={{
      padding: '3.5rem 2rem',
      maxWidth: '750px',
      margin: '0 auto',
      textAlign: 'center',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '2.25rem',
    }}>
      {/* Workflow Stepper in Processing */}
      <div className="workflow-stepper" style={{ width: '100%', marginBottom: '0.5rem' }}>
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
        <div className="stepper-item active">
          <div className="stepper-circle">3</div>
          <span>3. Neural Inference</span>
        </div>
        <div className="stepper-divider" />
        <div className="stepper-item">
          <div className="stepper-circle">4</div>
          <span>4. Results</span>
        </div>
      </div>

      {/* Animated Radar Scanner */}
      <div style={{ position: 'relative', width: '150px', height: '150px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="radar-spinner" />
        
        <div style={{
          position: 'absolute',
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #06b6d4 0%, #6366f1 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 30px rgba(6, 182, 212, 0.65)',
          animation: 'pulse-glow 2s infinite',
        }}>
          <Cpu size={32} color="#ffffff" />
        </div>
      </div>

      {/* Progress Info */}
      <div style={{ width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
          <span style={{ fontSize: '0.92rem', color: '#38bdf8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={16} /> {stepLabel || 'Deep Learning Pipeline Active...'}
          </span>
          <span style={{ fontSize: '1.3rem', fontWeight: 900, color: 'var(--accent-cyan)' }}>
            {progress}%
          </span>
        </div>

        {/* Progress Bar Track */}
        <div style={{
          width: '100%',
          height: '10px',
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '999px',
          overflow: 'hidden',
          border: '1px solid rgba(255, 255, 255, 0.08)',
        }}>
          <div style={{
            height: '100%',
            width: `${progress}%`,
            background: 'linear-gradient(90deg, #38bdf8 0%, #06b6d4 50%, #10b981 100%)',
            borderRadius: '999px',
            transition: 'width 0.4s ease',
            boxShadow: '0 0 16px rgba(6, 182, 212, 0.7)',
          }} />
        </div>
      </div>

      {/* Pipeline Checklist */}
      <div style={{
        width: '100%',
        background: 'rgba(13, 21, 39, 0.7)',
        borderRadius: 'var(--radius-md)',
        padding: '1.35rem 1.75rem',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        textAlign: 'left',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.1rem' }}>
          <Sparkles size={16} color="var(--accent-cyan)" />
          <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)' }}>
            Deep Learning Inference Sequence:
          </h4>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {PEDIATRIC_DL_STEPS.map((label, index) => {
            const stepNum = index + 1;
            const isDone = currentStep > stepNum;
            const isActive = currentStep === stepNum;

            return (
              <div
                key={index}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.85rem',
                  fontSize: '0.86rem',
                  color: isDone ? '#34d399' : isActive ? '#38bdf8' : 'var(--text-subtle)',
                  fontWeight: isActive ? 700 : 400,
                  transition: 'all 0.2s ease',
                }}
              >
                {isDone ? (
                  <CheckCircle2 size={17} color="#10b981" />
                ) : isActive ? (
                  <Loader2 size={17} color="var(--accent-cyan)" style={{ animation: 'spin 1.5s linear infinite' }} />
                ) : (
                  <div style={{ width: '17px', height: '17px', borderRadius: '50%', border: '1px solid var(--text-subtle)' }} />
                )}
                <span>{label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {onCancel && (
        <button
          onClick={onCancel}
          className="btn-secondary"
          style={{
            fontSize: '0.86rem',
            padding: '0.55rem 1.25rem',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            marginTop: '0.5rem',
          }}
        >
          Cancel Screening
        </button>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
