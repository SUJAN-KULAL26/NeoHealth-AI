import React, { useState } from 'react';
import { Eye, Sliders, Layers, Grid, Sparkles, Target, SplitSquareVertical } from 'lucide-react';
import type { GradCAMData } from '../types/screening';

interface GradCAMViewerProps {
  gradCAM: GradCAMData;
}

type ViewMode = 'overlay' | 'split' | 'slider' | 'original';

export const GradCAMViewer: React.FC<GradCAMViewerProps> = ({ gradCAM }) => {
  const [viewMode, setViewMode] = useState<ViewMode>('overlay');
  const [opacity, setOpacity] = useState<number>(gradCAM.opacityDefault || 0.75);
  const [sliderPosition, setSliderPosition] = useState<number>(50);
  const [showRoi, setShowRoi] = useState<boolean>(true);

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      {/* Header & Mode Controls */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '1.5rem',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={20} color="var(--accent-cyan)" />
            <h3 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Grad-CAM Visual Explainability Map</h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Convolutional gradient spatial activation highlighting features driving model decision.
          </p>
        </div>

        {/* View Mode Selector Tabs */}
        <div style={{
          display: 'flex',
          background: 'rgba(13, 21, 39, 0.85)',
          padding: '0.3rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          gap: '0.25rem',
          flexWrap: 'wrap',
        }}>
          <button
            onClick={() => setViewMode('overlay')}
            style={{
              background: viewMode === 'overlay' ? 'var(--accent-cyan)' : 'transparent',
              color: viewMode === 'overlay' ? '#ffffff' : 'var(--text-muted)',
              border: 'none',
              padding: '0.45rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              transition: 'all 0.2s ease',
            }}
          >
            <Layers size={14} /> Overlay
          </button>

          <button
            onClick={() => setViewMode('slider')}
            style={{
              background: viewMode === 'slider' ? 'var(--accent-cyan)' : 'transparent',
              color: viewMode === 'slider' ? '#ffffff' : 'var(--text-muted)',
              border: 'none',
              padding: '0.45rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              transition: 'all 0.2s ease',
            }}
          >
            <SplitSquareVertical size={14} /> Split Slider
          </button>

          <button
            onClick={() => setViewMode('split')}
            style={{
              background: viewMode === 'split' ? 'var(--accent-cyan)' : 'transparent',
              color: viewMode === 'split' ? '#ffffff' : 'var(--text-muted)',
              border: 'none',
              padding: '0.45rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              transition: 'all 0.2s ease',
            }}
          >
            <Grid size={14} /> Side-by-Side
          </button>

          <button
            onClick={() => setViewMode('original')}
            style={{
              background: viewMode === 'original' ? 'var(--accent-cyan)' : 'transparent',
              color: viewMode === 'original' ? '#ffffff' : 'var(--text-muted)',
              border: 'none',
              padding: '0.45rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              transition: 'all 0.2s ease',
            }}
          >
            <Eye size={14} /> Original
          </button>
        </div>
      </div>

      {/* Main Image Display Container */}
      {viewMode === 'split' ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', marginBottom: '1.25rem' }}>
          <div>
            <span style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
              Original Clinical Scan
            </span>
            <div style={{ height: '340px', borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <img src={gradCAM.originalImage} alt="Original" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </div>
          </div>

          <div>
            <span style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '0.5rem' }}>
              Grad-CAM Activation Heatmap
            </span>
            <div style={{ height: '340px', borderRadius: 'var(--radius-md)', overflow: 'hidden', border: '1px solid rgba(6, 182, 212, 0.4)' }}>
              <img src={gradCAM.heatmapOverlay} alt="Heatmap" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </div>
          </div>
        </div>
      ) : viewMode === 'slider' ? (
        <div style={{
          position: 'relative',
          width: '100%',
          height: '380px',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          border: '1px solid rgba(6, 182, 212, 0.4)',
          marginBottom: '1.25rem',
          boxShadow: '0 12px 35px rgba(0, 0, 0, 0.65)',
        }}>
          {/* Base: Heatmap */}
          <img
            src={gradCAM.heatmapOverlay}
            alt="Heatmap"
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }}
          />

          {/* Top Layer: Original (Clipped by slider position) */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: `${sliderPosition}%`,
            height: '100%',
            overflow: 'hidden',
            borderRight: '2px solid #ffffff',
            boxShadow: '4px 0 15px rgba(0, 0, 0, 0.5)',
          }}>
            <img
              src={gradCAM.originalImage}
              alt="Original"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                maxWidth: 'none',
                height: '100%',
                objectFit: 'cover',
                minWidth: '700px', // Maintain aspect
              }}
            />
          </div>

          {/* Slider drag control */}
          <div style={{
            position: 'absolute',
            bottom: '1rem',
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'rgba(7, 11, 20, 0.85)',
            padding: '0.5rem 1rem',
            borderRadius: '999px',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            width: '80%',
            maxWidth: '350px',
            backdropFilter: 'blur(8px)',
          }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Original</span>
            <input
              type="range"
              min="0"
              max="100"
              value={sliderPosition}
              onChange={(e) => setSliderPosition(Number(e.target.value))}
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>Grad-CAM</span>
          </div>
        </div>
      ) : (
        <div style={{
          position: 'relative',
          width: '100%',
          height: '380px',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          border: '1px solid rgba(6, 182, 212, 0.35)',
          marginBottom: '1.25rem',
          boxShadow: '0 12px 35px rgba(0, 0, 0, 0.65)',
        }}>
          {/* Base Original Image */}
          <img
            src={gradCAM.originalImage}
            alt="Original Scan"
            style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover' }}
          />

          {/* Heatmap Layer */}
          {viewMode === 'overlay' && (
            <img
              src={gradCAM.heatmapOverlay}
              alt="Grad-CAM Layer"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                opacity: opacity,
                mixBlendMode: 'screen',
                transition: 'opacity 0.15s ease',
              }}
            />
          )}

          {/* Target ROI Marker Overlays */}
          {showRoi && viewMode !== 'original' && gradCAM.regionsOfInterest?.map((roi, idx) => (
            <div
              key={idx}
              style={{
                position: 'absolute',
                left: `${roi.x * 100}%`,
                top: `${roi.y * 100}%`,
                transform: 'translate(-50%, -50%)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                background: 'rgba(7, 11, 20, 0.85)',
                padding: '0.35rem 0.75rem',
                borderRadius: '999px',
                border: '1px solid rgba(6, 182, 212, 0.7)',
                fontSize: '0.75rem',
                color: '#ffffff',
                fontWeight: 600,
                pointerEvents: 'none',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.6)',
              }}
            >
              <Target size={13} color="var(--accent-cyan)" />
              <span>{roi.label} ({Math.round(roi.intensity * 100)}%)</span>
            </div>
          ))}
        </div>
      )}

      {/* Control Panel: Opacity Slider, ROI Toggle, and Spectrum Legend */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(13, 21, 39, 0.7)',
        padding: '1.1rem 1.4rem',
        borderRadius: 'var(--radius-md)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        flexWrap: 'wrap',
        gap: '1.25rem',
      }}>
        {viewMode === 'overlay' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', minWidth: '260px', flex: '1 1 280px' }}>
            <Sliders size={16} color="var(--accent-cyan)" />
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', fontWeight: 600 }}>
              Heatmap Intensity ({Math.round(opacity * 100)}%)
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={opacity}
              onChange={(e) => setOpacity(parseFloat(e.target.value))}
            />
          </div>
        )}

        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setShowRoi(!showRoi)}
            style={{
              background: showRoi ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255, 255, 255, 0.05)',
              border: showRoi ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.1)',
              color: showRoi ? 'var(--accent-cyan)' : 'var(--text-muted)',
              padding: '0.4rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <Target size={14} /> ROI Regions: {showRoi ? 'ON' : 'OFF'}
          </button>

          {/* Heat Spectrum Bar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.76rem', color: 'var(--text-subtle)' }}>
            <span>Low Gradient</span>
            <div style={{
              width: '130px',
              height: '8px',
              borderRadius: '4px',
              background: 'linear-gradient(90deg, #0032ff 0%, #00dcff 35%, #ffe600 70%, #ff0000 100%)',
              boxShadow: '0 0 10px rgba(255, 0, 0, 0.3)',
            }} />
            <span>High Activation</span>
          </div>
        </div>
      </div>
    </div>
  );
};
