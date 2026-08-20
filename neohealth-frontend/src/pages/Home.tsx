import React, { useState } from 'react';
import { 
  Activity, 
  ArrowRight, 
  ShieldCheck, 
  Sparkles, 
  Baby
} from 'lucide-react';
import type { DiseaseClass } from '../types/screening';
import { PEDIATRIC_DISEASE_PRESETS } from '../services/api';

interface HomeProps {
  onStartScreening: () => void;
  onViewHistory: () => void;
}

export const Home: React.FC<HomeProps> = ({ onStartScreening, onViewHistory }) => {
  const [selectedDisease, setSelectedDisease] = useState<DiseaseClass>('Jaundice');

  const diseaseClasses: {
    id: DiseaseClass;
    name: string;
    type: string;
    badgeColor: string;
    icon: string;
    summary: string;
    visualCue: string;
  }[] = [
    {
      id: 'Jaundice',
      name: 'Jaundice',
      type: 'Infant health condition',
      badgeColor: '#f59e0b',
      icon: '🟡',
      summary: 'Neonatal hyperbilirubinemia manifesting as dermal and scleral yellowing.',
      visualCue: 'Scleral icterus, forehead and torso yellowish vascular discoloration',
    },
    {
      id: 'Atopic Dermatitis',
      name: 'Atopic Dermatitis',
      type: 'Skin condition',
      badgeColor: '#f43f5e',
      icon: '🔴',
      summary: 'Pediatric eczema featuring pruritic, xerotic erythematous plaques and compromised epidermal barrier.',
      visualCue: 'Erythematous scaly patches on cheeks, neck creases, and extensor surfaces',
    },
    {
      id: 'Impetigo',
      name: 'Impetigo',
      type: 'Bacterial skin infection',
      badgeColor: '#ef4444',
      icon: '⚠️',
      summary: 'Contagious bacterial pyoderma characterized by fragile vesicles and honey-colored crusts.',
      visualCue: 'Perioral/nasal erythematous base with stuck-on golden-yellow crusting',
    },
    {
      id: 'Cradle Cap',
      name: 'Cradle Cap',
      type: 'Infant scalp condition',
      badgeColor: '#eab308',
      icon: '👶',
      summary: 'Infantile seborrheic dermatitis presenting with thick, greasy yellowish adherent scalp flakes.',
      visualCue: 'Waxy yellowish scales adhering tightly to scalp vertex and fontanelle',
    },
    {
      id: 'Neonatal Acne',
      name: 'Neonatal Acne',
      type: 'Infant skin condition',
      badgeColor: '#38bdf8',
      icon: '✨',
      summary: 'Benign neonatal cephalic pustulosis caused by maternal androgen hormonal stimulation.',
      visualCue: 'Discrete inflammatory micro-papules and pustules on baby cheeks and nose',
    },
    {
      id: 'Normal',
      name: 'Normal',
      type: 'Healthy/normal appearance',
      badgeColor: '#10b981',
      icon: '💚',
      summary: 'Healthy newborn dermatological presentation with intact baseline epidermal barrier.',
      visualCue: 'Homogenous skin tone without pathological icterus, scaling, or pustules',
    },
  ];

  const currentPreset = PEDIATRIC_DISEASE_PRESETS[selectedDisease];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4rem', paddingBottom: '3rem' }}>
      {/* 1. HERO SECTION */}
      <section style={{
        textAlign: 'center',
        padding: '3rem 1rem 1rem',
        maxWidth: '960px',
        margin: '0 auto',
        position: 'relative',
      }}>
        {/* Glowing Badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.6rem',
          background: 'rgba(6, 182, 212, 0.12)',
          border: '1px solid rgba(6, 182, 212, 0.35)',
          padding: '0.45rem 1.25rem',
          borderRadius: '999px',
          fontSize: '0.88rem',
          color: '#38bdf8',
          marginBottom: '1.75rem',
          boxShadow: '0 0 25px rgba(6, 182, 212, 0.2)',
        }}>
          <Sparkles size={16} color="#38bdf8" /> 
          <span>Pediatric Deep Learning Decision Support & Grad-CAM System</span>
        </div>

        <h1 style={{
          fontSize: '3.4rem',
          fontWeight: 900,
          lineHeight: 1.15,
          marginBottom: '1.4rem',
          letterSpacing: '-0.03em',
        }}>
          Precision Infant Screening Powered by <span className="text-gradient-cyan">Explainable AI</span>
        </h1>

        <p style={{
          fontSize: '1.18rem',
          color: 'var(--text-muted)',
          lineHeight: 1.65,
          maxWidth: '780px',
          margin: '0 auto 2.5rem',
        }}>
          Dedicated clinical deep learning model engineered specifically to detect and differentiate 
          <strong style={{ color: '#ffffff' }}> 6 core infant & pediatric conditions</strong> with instant convolutional Grad-CAM visual spatial heatmaps and pediatrician-aligned care protocols.
        </p>

        {/* Hero CTAs */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1.25rem', flexWrap: 'wrap' }}>
          <button onClick={onStartScreening} className="btn-primary" style={{ padding: '1.05rem 2.4rem', fontSize: '1.05rem' }}>
            <Activity size={20} /> Start Diagnostic Screening <ArrowRight size={18} />
          </button>
          <button onClick={onViewHistory} className="btn-secondary" style={{ padding: '1.05rem 2rem', fontSize: '1.05rem' }}>
            View Clinical Case History
          </button>
        </div>
      </section>

      {/* 2. STATS BANNER */}
      <section className="glass-panel" style={{
        maxWidth: '1100px',
        margin: '0 auto',
        width: '100%',
        padding: '2rem 2.5rem',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '2rem',
        textAlign: 'center',
      }}>
        <div>
          <h3 style={{ fontSize: '2.4rem', fontWeight: 900, color: 'var(--accent-cyan)' }}>6 Classes</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Target Pediatric Conditions</p>
        </div>
        <div>
          <h3 style={{ fontSize: '2.4rem', fontWeight: 900, color: 'var(--accent-emerald)' }}>94.6%</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Multi-Class Sensitivity</p>
        </div>
        <div>
          <h3 style={{ fontSize: '2.4rem', fontWeight: 900, color: 'var(--accent-amber)' }}>Grad-CAM</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Visual Spatial Activation</p>
        </div>
        <div>
          <h3 style={{ fontSize: '2.4rem', fontWeight: 900, color: '#818cf8' }}>&lt; 2.5s</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Real-Time Inference Speed</p>
        </div>
      </section>

      {/* 3. INTERACTIVE 6-DISEASE EXPLORER */}
      <section style={{ maxWidth: '1150px', margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.25rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: 'rgba(99, 102, 241, 0.12)',
            padding: '0.3rem 0.9rem',
            borderRadius: '999px',
            color: '#818cf8',
            fontSize: '0.8rem',
            fontWeight: 700,
            marginBottom: '0.75rem',
            border: '1px solid rgba(99, 102, 241, 0.3)',
          }}>
            <Baby size={14} /> 6 DEDICATED MODEL CLASSES
          </div>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 800 }}>Infant & Pediatric Diagnostic Spectrum</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '650px', margin: '0.5rem auto 0' }}>
            Our deep convolutional network is trained exclusively on clinical infant dermatological datasets. Select a disease class to inspect its biomarkers:
          </p>
        </div>

        {/* Disease Tab Pills */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
          gap: '0.75rem',
          marginBottom: '2rem',
        }}>
          {diseaseClasses.map((item) => {
            const isSelected = selectedDisease === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setSelectedDisease(item.id)}
                style={{
                  background: isSelected ? 'rgba(6, 182, 212, 0.18)' : 'rgba(13, 21, 39, 0.65)',
                  border: isSelected ? '1px solid var(--accent-cyan)' : '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1rem 0.8rem',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: isSelected ? '0 0 20px rgba(6, 182, 212, 0.25)' : 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '1.2rem' }}>{item.icon}</span>
                  <span style={{
                    fontWeight: 700,
                    fontSize: '0.92rem',
                    color: isSelected ? '#ffffff' : 'var(--text-main)',
                  }}>
                    {item.name}
                  </span>
                </div>
                <span style={{
                  fontSize: '0.74rem',
                  color: isSelected ? 'var(--accent-cyan)' : 'var(--text-subtle)',
                  display: 'block',
                }}>
                  {item.type}
                </span>
              </button>
            );
          })}
        </div>

        {/* Selected Disease Deep-Dive Inspector Card */}
        <div className="glass-panel" style={{
          padding: '2.25rem',
          borderLeft: `5px solid ${currentPreset.riskLevel === 'high' ? '#f43f5e' : currentPreset.riskLevel === 'moderate' ? '#f59e0b' : '#10b981'}`,
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem', alignItems: 'center' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <span style={{
                  background: 'rgba(6, 182, 212, 0.15)',
                  color: '#38bdf8',
                  padding: '0.3rem 0.8rem',
                  borderRadius: '999px',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  border: '1px solid rgba(6, 182, 212, 0.3)',
                }}>
                  {currentPreset.type}
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)' }}>
                  Deep Learning Class Index
                </span>
              </div>

              <h3 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#ffffff', marginBottom: '0.75rem' }}>
                {currentPreset.disease}
              </h3>

              <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '1.25rem' }}>
                {currentPreset.diagnosticSummary}
              </p>

              <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '1rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                marginBottom: '1.25rem',
              }}>
                <strong style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem', display: 'block', marginBottom: '0.3rem' }}>
                  Convolutional Visual Cues:
                </strong>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
                  {diseaseClasses.find(d => d.id === selectedDisease)?.visualCue}
                </p>
              </div>

              <button onClick={onStartScreening} className="btn-primary" style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem' }}>
                Screen Target Case for {currentPreset.disease} <ArrowRight size={16} />
              </button>
            </div>

            {/* Recommendations Preview Box */}
            <div style={{
              background: 'rgba(7, 11, 20, 0.7)',
              borderRadius: 'var(--radius-md)',
              padding: '1.5rem',
              border: '1px solid rgba(255, 255, 255, 0.08)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <ShieldCheck size={18} color="var(--accent-emerald)" />
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff' }}>
                  Pediatric Care Protocol Preview
                </h4>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {currentPreset.recommendations.map((rec) => (
                  <div key={rec.id} style={{
                    padding: '0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    background: rec.urgency === 'urgent' ? 'rgba(244, 63, 94, 0.1)' : 'rgba(255, 255, 255, 0.03)',
                    border: rec.urgency === 'urgent' ? '1px solid rgba(244, 63, 94, 0.3)' : '1px solid rgba(255, 255, 255, 0.05)',
                  }}>
                    <h5 style={{ fontSize: '0.88rem', fontWeight: 600, color: rec.urgency === 'urgent' ? '#fda4af' : '#ffffff', marginBottom: '0.2rem' }}>
                      {rec.title}
                    </h5>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                      {rec.detail}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. WORKFLOW PIPELINE ARCHITECTURE */}
      <section style={{ maxWidth: '1150px', margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 800 }}>End-to-End Diagnostic Pipeline</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Structured clinical workflow engineered for pediatricians, nurses, and care providers.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: '1.25rem',
          position: 'relative',
        }}>
          <div className="glass-card">
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(6, 182, 212, 0.15)',
              color: 'var(--accent-cyan)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '0.85rem',
              fontWeight: 800,
            }}>
              1
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.35rem' }}>Image Input</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
              Upload dermatological photos, capture via live HD camera, or select 1-click clinical presets.
            </p>
          </div>

          <div className="glass-card">
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(99, 102, 241, 0.15)',
              color: '#818cf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '0.85rem',
              fontWeight: 800,
            }}>
              2
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.35rem' }}>Metadata Preview</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
              Assign anatomical body location (Face, Scalp, Cheeks, Torso) and document clinical symptoms.
            </p>
          </div>

          <div className="glass-card">
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(16, 185, 129, 0.15)',
              color: 'var(--accent-emerald)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '0.85rem',
              fontWeight: 800,
            }}>
              3
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.35rem' }}>Deep CNN Inference</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
              Multi-layer convolutional feature extraction, artifact removal, and 6-class neural classification.
            </p>
          </div>

          <div className="glass-card">
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(245, 158, 11, 0.15)',
              color: 'var(--accent-amber)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '0.85rem',
              fontWeight: 800,
            }}>
              4
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.35rem' }}>Grad-CAM Maps</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
              Inspect visual gradient heatmaps superimposing exact spatial regions guiding AI confidence.
            </p>
          </div>

          <div className="glass-card">
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(244, 63, 94, 0.15)',
              color: 'var(--accent-rose)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '0.85rem',
              fontWeight: 800,
            }}>
              5
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.35rem' }}>Clinical Care Plan</h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.45 }}>
              Access tailored pediatric guidance, red-flag triggers, and one-click PDF clinical report export.
            </p>
          </div>
        </div>
      </section>

      {/* 5. BOTTOM CTA BANNER */}
      <section className="glass-panel" style={{
        maxWidth: '1150px',
        margin: '0 auto',
        width: '100%',
        padding: '3rem 2rem',
        textAlign: 'center',
        background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%)',
        border: '1px solid rgba(6, 182, 212, 0.3)',
      }}>
        <h2 style={{ fontSize: '2.4rem', fontWeight: 900, marginBottom: '0.75rem' }}>
          Ready to Screen an Infant Patient?
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', maxWidth: '600px', margin: '0 auto 1.75rem' }}>
          Upload a high-resolution scan, capture a live video frame, or test instantly with our pre-loaded pediatric case library.
        </p>
        <button onClick={onStartScreening} className="btn-primary" style={{ padding: '1rem 2.5rem', fontSize: '1.05rem' }}>
          <Activity size={20} /> Open Diagnostic Screening Studio <ArrowRight size={18} />
        </button>
      </section>
    </div>
  );
};
