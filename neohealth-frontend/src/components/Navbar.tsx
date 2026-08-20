import React from 'react';
import { Activity, ShieldCheck, Home, PlusCircle, History } from 'lucide-react';
import type { PageName } from '../hooks/useScreening';

interface NavbarProps {
  activePage: PageName;
  onNavigate: (page: PageName) => void;
  onNewScreening: () => void;
  historyCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  activePage,
  onNavigate,
  onNewScreening,
  historyCount,
}) => {
  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      background: 'rgba(7, 11, 20, 0.88)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      padding: '0.85rem 2rem',
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Brand Logo */}
        <div 
          onClick={() => onNavigate('home')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', cursor: 'pointer' }}
        >
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #06b6d4 0%, #6366f1 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(6, 182, 212, 0.45)',
          }}>
            <Activity size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <span style={{ fontSize: '1.3rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif' }}>
                Neo<span className="text-gradient-cyan">Health</span> <span style={{ color: '#818cf8' }}>AI</span>
              </span>
              <span style={{
                fontSize: '0.68rem',
                fontWeight: 700,
                background: 'rgba(6, 182, 212, 0.15)',
                color: '#38bdf8',
                padding: '0.15rem 0.5rem',
                borderRadius: '999px',
                border: '1px solid rgba(6, 182, 212, 0.3)',
                letterSpacing: '0.04em',
              }}>
                6-CLASS PEDIATRIC DL
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Infant Diagnostic Decision Support & Grad-CAM</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            onClick={() => onNavigate('home')}
            style={{
              background: activePage === 'home' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              border: activePage === 'home' ? '1px solid rgba(255, 255, 255, 0.15)' : '1px solid transparent',
              color: activePage === 'home' ? '#ffffff' : 'var(--text-muted)',
              padding: '0.6rem 1.1rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.9rem',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              transition: 'all 0.2s ease',
            }}
          >
            <Home size={16} /> Home
          </button>

          <button
            onClick={onNewScreening}
            style={{
              background: activePage === 'screening' || activePage === 'processing'
                ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(99, 102, 241, 0.25) 100%)'
                : 'transparent',
              border: activePage === 'screening' || activePage === 'processing'
                ? '1px solid rgba(6, 182, 212, 0.45)'
                : '1px solid transparent',
              color: activePage === 'screening' || activePage === 'processing' ? '#38bdf8' : 'var(--text-muted)',
              padding: '0.6rem 1.1rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              transition: 'all 0.2s ease',
            }}
          >
            <PlusCircle size={16} /> Diagnostic Screening
          </button>

          <button
            onClick={() => onNavigate('history')}
            style={{
              background: activePage === 'history' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              border: activePage === 'history' ? '1px solid rgba(255, 255, 255, 0.15)' : '1px solid transparent',
              color: activePage === 'history' ? '#ffffff' : 'var(--text-muted)',
              padding: '0.6rem 1.1rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.9rem',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              transition: 'all 0.2s ease',
            }}
          >
            <History size={16} /> Case History
            {historyCount > 0 && (
              <span style={{
                background: 'rgba(6, 182, 212, 0.25)',
                color: '#38bdf8',
                fontSize: '0.72rem',
                fontWeight: 700,
                padding: '0.1rem 0.45rem',
                borderRadius: '999px',
                marginLeft: '0.2rem',
              }}>
                {historyCount}
              </span>
            )}
          </button>
        </nav>

        {/* System Status Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            background: 'rgba(16, 185, 129, 0.12)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            padding: '0.4rem 0.85rem',
            borderRadius: '999px',
            fontSize: '0.8rem',
            color: '#34d399',
            fontWeight: 600,
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#10b981',
              boxShadow: '0 0 10px #10b981',
            }} />
            <ShieldCheck size={14} /> CNN Model Live
          </div>
        </div>
      </div>
    </header>
  );
};
