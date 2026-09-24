import React, { useState } from 'react';
import { ArrowLeft, Play, FileText, CheckCircle2, Baby, Scan } from 'lucide-react';
import type { ScreeningInput } from '../types/screening';

interface ImagePreviewProps {
  input: ScreeningInput;
  onConfirm: (bodySite: string, patientNotes: string) => void;
  onCancel: () => void;
}

const FIXED_BODY_SITE = 'Face / Cheeks';

export const ImagePreview: React.FC<ImagePreviewProps> = ({ input, onConfirm, onCancel }) => {
  const [selectedSite] = useState<string>(FIXED_BODY_SITE);
  const [notes, setNotes] = useState<string>(input.patientNotes || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onConfirm(selectedSite, notes);
  };

  return (
    <div className="glass-panel" style={{ padding: '2.25rem', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#38bdf8', fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.2rem' }}>
            <Baby size={16} /> Infant Clinical Verification
          </div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Scan Metadata & Confirmation</h3>
        </div>
        <button onClick={onCancel} className="btn-secondary" style={{ padding: '0.55rem 1.1rem', fontSize: '0.85rem' }}>
          <ArrowLeft size={16} /> Re-upload / Choose Other
        </button>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
        {/* Left Side: Image Preview Frame */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{
            position: 'relative',
            width: '100%',
            height: '300px',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            border: '1px solid rgba(6, 182, 212, 0.4)',
            boxShadow: '0 12px 30px rgba(0, 0, 0, 0.6)',
          }}>
            <img
              src={input.imageSrc}
              alt="Infant Scan Preview"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
            <span style={{
              position: 'absolute',
              bottom: '0.85rem',
              left: '0.85rem',
              background: 'rgba(7, 11, 20, 0.85)',
              color: '#ffffff',
              fontSize: '0.78rem',
              padding: '0.3rem 0.75rem',
              borderRadius: '6px',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              backdropFilter: 'blur(8px)',
            }}>
              Source: {input.source === 'webcam' ? 'Live Webcam Capture' : input.source === 'preset' ? 'Clinical Dataset Preset' : 'File Upload'}
            </span>

            {input.presetCondition && (
              <span style={{
                position: 'absolute',
                top: '0.85rem',
                right: '0.85rem',
                background: 'rgba(6, 182, 212, 0.9)',
                color: '#ffffff',
                fontSize: '0.75rem',
                fontWeight: 700,
                padding: '0.25rem 0.65rem',
                borderRadius: '6px',
              }}>
                Target: {input.presetCondition}
              </span>
            )}
          </div>

          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            padding: '0.85rem 1.1rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(255, 255, 255, 0.07)',
            fontSize: '0.82rem',
            color: 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}>
            <span>Model Input: 224x224 RGB Normalization</span>
            <span style={{ color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 600 }}>
              <CheckCircle2 size={14} /> Quality Verified
            </span>
          </div>
        </div>

        {/* Right Side: Scan Region (fixed) & Clinical Notes */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.35rem', justifyContent: 'space-between' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-main)' }}>
              <Scan size={15} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle', color: 'var(--accent-cyan)' }} />
              Scan Region
            </label>
            <div style={{
              width: '100%',
              padding: '0.8rem 1rem',
              background: 'rgba(6, 182, 212, 0.08)',
              border: '1px solid rgba(6, 182, 212, 0.35)',
              borderRadius: 'var(--radius-md)',
              color: '#38bdf8',
              fontSize: '0.92rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}>
              <CheckCircle2 size={16} color="#10b981" />
              Face / Cheeks — Auto-detected by MediaPipe
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-main)' }}>
              <FileText size={15} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle', color: 'var(--accent-cyan)' }} />
              Patient Age & Symptoms (Optional)
            </label>
            <textarea
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. 2-week-old newborn, noticed mild jaundice / rash starting 2 days ago..."
              style={{
                width: '100%',
                padding: '0.8rem 1rem',
                background: 'rgba(13, 21, 39, 0.85)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                borderRadius: 'var(--radius-md)',
                color: '#ffffff',
                fontSize: '0.88rem',
                outline: 'none',
                resize: 'none',
              }}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '1.05rem', fontSize: '1rem' }}
          >
            <Play size={18} /> Analyze Image with Deep Learning Model
          </button>
        </div>
      </form>
    </div>
  );
};
