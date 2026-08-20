import React, { useState } from 'react';
import { UploadCloud, Camera, ArrowLeft, Sparkles, FolderOpen, Play, CheckCircle2 } from 'lucide-react';
import { ImageUploader } from '../components/ImageUploader';
import { WebcamCapture } from '../components/WebcamCapture';
import { ImagePreview } from '../components/ImagePreview';
import { ErrorMessage } from '../components/ErrorMessage';
import type { ScreeningInput, DiseaseClass } from '../types/screening';
import { QUICK_TEST_SAMPLES } from '../services/api';

interface ScreeningProps {
  input: ScreeningInput | null;
  error: string | null;
  onSetImageInput: (
    imageSrc: string, 
    source: 'upload' | 'webcam' | 'preset', 
    bodySite?: string, 
    patientNotes?: string, 
    file?: File, 
    presetCondition?: DiseaseClass
  ) => boolean;
  onConfirmAndStart: (bodySite: string, patientNotes: string) => void;
  onCancelInput: () => void;
  onDismissError: () => void;
  onNavigateHome: () => void;
}

type TabType = 'upload' | 'webcam' | 'samples';

export const Screening: React.FC<ScreeningProps> = ({
  input,
  error,
  onSetImageInput,
  onConfirmAndStart,
  onCancelInput,
  onDismissError,
  onNavigateHome,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('upload');

  const handleImageSelected = (imageSrc: string, file?: File) => {
    onSetImageInput(imageSrc, activeTab === 'webcam' ? 'webcam' : 'upload', 'Face / Cheeks', '', file);
  };

  const handleSampleSelected = (sample: typeof QUICK_TEST_SAMPLES[0]) => {
    onSetImageInput(
      sample.imageSrc,
      'preset',
      sample.defaultSite,
      sample.notes,
      undefined,
      sample.condition
    );
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Visual Workflow Stepper */}
      <div className="workflow-stepper">
        <div className={`stepper-item ${!input ? 'active' : 'completed'}`}>
          <div className="stepper-circle">{input ? <CheckCircle2 size={16} /> : '1'}</div>
          <span>1. Image Input</span>
        </div>
        <div className="stepper-divider" />
        <div className={`stepper-item ${input ? 'active' : ''}`}>
          <div className="stepper-circle">2</div>
          <span>2. Metadata & Preview</span>
        </div>
        <div className="stepper-divider" />
        <div className="stepper-item">
          <div className="stepper-circle">3</div>
          <span>3. Neural Inference</span>
        </div>
        <div className="stepper-divider" />
        <div className="stepper-item">
          <div className="stepper-circle">4</div>
          <span>4. Grad-CAM & Plan</span>
        </div>
      </div>

      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
            <span style={{
              background: 'rgba(6, 182, 212, 0.15)',
              color: '#38bdf8',
              padding: '0.2rem 0.6rem',
              borderRadius: '999px',
              fontSize: '0.75rem',
              fontWeight: 700,
            }}>
              STEP {input ? '2 OF 4' : '1 OF 4'}
            </span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-subtle)' }}>• Infant Diagnostic Acquisition</span>
          </div>
          <h2 style={{ fontSize: '1.9rem', fontWeight: 800 }}>Pediatric Screening Studio</h2>
        </div>

        <button onClick={onNavigateHome} className="btn-secondary" style={{ fontSize: '0.88rem', padding: '0.6rem 1.1rem' }}>
          <ArrowLeft size={16} /> Back to Overview
        </button>
      </div>

      {/* Error Alert */}
      {error && <ErrorMessage message={error} onDismiss={onDismissError} />}

      {/* Main Content Area */}
      {input ? (
        <ImagePreview
          input={input}
          onConfirm={(bodySite, notes) => {
            onConfirmAndStart(bodySite, notes);
          }}
          onCancel={onCancelInput}
        />
      ) : (
        <div className="glass-panel" style={{ padding: '2.25rem' }}>
          {/* Mode Switcher Tabs */}
          <div style={{
            display: 'flex',
            maxWidth: '520px',
            margin: '0 auto 2rem',
            background: 'rgba(13, 21, 39, 0.85)',
            padding: '0.35rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            gap: '0.25rem',
          }}>
            <button
              onClick={() => setActiveTab('upload')}
              style={{
                flex: 1,
                padding: '0.75rem 0.8rem',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                background: activeTab === 'upload' ? 'var(--accent-cyan)' : 'transparent',
                color: activeTab === 'upload' ? '#ffffff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.88rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.45rem',
                transition: 'all 0.2s ease',
              }}
            >
              <UploadCloud size={17} /> File Upload
            </button>

            <button
              onClick={() => setActiveTab('webcam')}
              style={{
                flex: 1,
                padding: '0.75rem 0.8rem',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                background: activeTab === 'webcam' ? 'var(--accent-cyan)' : 'transparent',
                color: activeTab === 'webcam' ? '#ffffff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.88rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.45rem',
                transition: 'all 0.2s ease',
              }}
            >
              <Camera size={17} /> Live Camera
            </button>

            <button
              onClick={() => setActiveTab('samples')}
              style={{
                flex: 1,
                padding: '0.75rem 0.8rem',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                background: activeTab === 'samples' ? 'var(--accent-cyan)' : 'transparent',
                color: activeTab === 'samples' ? '#ffffff' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.88rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.45rem',
                transition: 'all 0.2s ease',
              }}
            >
              <FolderOpen size={17} /> Quick-Test (6 Classes)
            </button>
          </div>

          {/* Tab 1: Upload */}
          {activeTab === 'upload' && (
            <ImageUploader
              onImageSelected={handleImageSelected}
              onError={() => onSetImageInput('', 'upload')}
            />
          )}

          {/* Tab 2: Live Webcam */}
          {activeTab === 'webcam' && (
            <WebcamCapture
              onCapture={(imageSrc) => handleImageSelected(imageSrc)}
              onError={(msg) => console.error(msg)}
            />
          )}

          {/* Tab 3: Quick-Test Presets for all 6 target classes */}
          {activeTab === 'samples' && (
            <div>
              <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: '#38bdf8', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.3rem' }}>
                  <Sparkles size={16} /> Instant Deep Learning Demonstration
                </div>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Select a 6-Class Infant Sample</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Click any verified clinical photo below to immediately load and evaluate the model:
                </p>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '1.25rem',
              }}>
                {QUICK_TEST_SAMPLES.map((sample) => (
                  <div
                    key={sample.id}
                    onClick={() => handleSampleSelected(sample)}
                    className="glass-card"
                    style={{
                      cursor: 'pointer',
                      display: 'flex',
                      gap: '1rem',
                      alignItems: 'center',
                      padding: '1rem',
                    }}
                  >
                    <div style={{
                      width: '72px',
                      height: '72px',
                      borderRadius: 'var(--radius-sm)',
                      overflow: 'hidden',
                      flexShrink: 0,
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                    }}>
                      <img
                        src={sample.imageSrc}
                        alt={sample.title}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    </div>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <span style={{
                        display: 'inline-block',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        color: 'var(--accent-cyan)',
                        marginBottom: '0.2rem',
                      }}>
                        {sample.condition}
                      </span>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {sample.title}
                      </h4>
                      <p style={{ fontSize: '0.76rem', color: 'var(--text-subtle)', marginTop: '0.2rem' }}>
                        {sample.category}
                      </p>
                    </div>

                    <div style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      background: 'rgba(6, 182, 212, 0.15)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--accent-cyan)',
                    }}>
                      <Play size={14} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
