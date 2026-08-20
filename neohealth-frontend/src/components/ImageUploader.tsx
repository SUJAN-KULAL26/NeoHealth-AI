import React, { useState, useRef } from 'react';
import { UploadCloud, Sparkles, FileCheck } from 'lucide-react';

interface ImageUploaderProps {
  onImageSelected: (imageSrc: string, file?: File) => void;
  onError: (msg: string) => void;
}

// High quality medical demo sample images for quick testing
const DEMO_SAMPLES = [
  {
    name: 'Sample A: Pigmented Mole',
    type: 'Nevus',
    url: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=600&auto=format&fit=crop&q=80',
  },
  {
    name: 'Sample B: Asymmetric Spot',
    type: 'Melanoma Risk',
    url: 'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=600&auto=format&fit=crop&q=80',
  },
  {
    name: 'Sample C: Irregular Keratosis',
    type: 'Keratosis',
    url: 'https://images.unsplash.com/photo-1516549655169-df83a0774514?w=600&auto=format&fit=crop&q=80',
  },
];

export const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageSelected, onError }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      onError('Please upload a valid image file (JPEG, PNG, WebP).');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const src = event.target?.result as string;
      if (src) {
        onImageSelected(src, file);
      }
    };
    reader.onerror = () => {
      onError('Failed to read selected image file.');
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Dropzone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: isDragging ? '2px dashed var(--accent-cyan)' : '2px dashed rgba(255, 255, 255, 0.15)',
          background: isDragging ? 'rgba(6, 182, 212, 0.08)' : 'rgba(15, 23, 42, 0.5)',
          borderRadius: 'var(--radius-lg)',
          padding: '3rem 2rem',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.25s ease',
          boxShadow: isDragging ? '0 0 25px rgba(6, 182, 212, 0.2)' : 'none',
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/jpeg,image/png,image/webp"
          style={{ display: 'none' }}
        />

        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          background: 'rgba(6, 182, 212, 0.12)',
          color: 'var(--accent-cyan)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1.25rem',
          border: '1px solid rgba(6, 182, 212, 0.25)',
        }}>
          <UploadCloud size={32} />
        </div>

        <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '0.5rem' }}>
          Drag & Drop Medical Image Here
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
          or <span style={{ color: 'var(--accent-cyan)', fontWeight: 600, textDecoration: 'underline' }}>Browse files</span> from your computer
        </p>

        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '1rem',
          padding: '0.5rem 1rem',
          background: 'rgba(255, 255, 255, 0.03)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          fontSize: '0.8rem',
          color: 'var(--text-subtle)',
        }}>
          <span><FileCheck size={13} style={{ display: 'inline', marginRight: '4px' }} /> JPEG, PNG, WebP</span>
          <span>•</span>
          <span>Max file size: 15MB</span>
          <span>•</span>
          <span>High Contrast & In-Focus Recommended</span>
        </div>
      </div>

      {/* Demo Quick-Load Samples */}
      <div className="glass-card" style={{ marginTop: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <Sparkles size={16} color="var(--accent-cyan)" />
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Or test instantly with sample clinical images:</h4>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {DEMO_SAMPLES.map((sample, idx) => (
            <div
              key={idx}
              onClick={() => onImageSelected(sample.url)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '0.6rem 0.8rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--accent-cyan)';
                e.currentTarget.style.background = 'rgba(6, 182, 212, 0.08)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
              }}
            >
              <img
                src={sample.url}
                alt={sample.name}
                style={{ width: '44px', height: '44px', borderRadius: '8px', objectFit: 'cover' }}
              />
              <div>
                <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>{sample.name}</p>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sample.type}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
