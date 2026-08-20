import React, { useState } from 'react';
import { History as HistoryIcon, Search, Trash2, Eye, PlusCircle, Calendar, Filter } from 'lucide-react';
import type { ScreeningHistoryItem } from '../types/screening';
import { formatDate, formatPercentage, getRiskColor } from '../utils/validation';

interface HistoryProps {
  history: ScreeningHistoryItem[];
  onSelectHistoryItem: (item: ScreeningHistoryItem) => void;
  onDeleteItem: (id: string) => void;
  onClearAll: () => void;
  onNewScreening: () => void;
}

export const History: React.FC<HistoryProps> = ({
  history,
  onSelectHistoryItem,
  onDeleteItem,
  onClearAll,
  onNewScreening,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRiskFilter, setSelectedRiskFilter] = useState<string>('all');

  const filteredHistory = history.filter((item) => {
    const matchesSearch =
      item.primaryPrediction.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.bodySite.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.id.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRisk = selectedRiskFilter === 'all' || item.riskLevel === selectedRiskFilter;

    return matchesSearch && matchesRisk;
  });

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem', paddingBottom: '3rem' }}>
      {/* Header & Quick Action */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800 }}>Screening History Log</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
            Archived diagnostic scans and AI inference records saved locally.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {history.length > 0 && (
            <button onClick={onClearAll} className="btn-secondary" style={{ fontSize: '0.85rem' }}>
              <Trash2 size={15} color="var(--accent-rose)" /> Clear All Log
            </button>
          )}
          <button onClick={onNewScreening} className="btn-primary" style={{ fontSize: '0.85rem', padding: '0.6rem 1.25rem' }}>
            <PlusCircle size={16} /> New Screening
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel" style={{ padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        {/* Search Bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          background: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 'var(--radius-md)',
          padding: '0.5rem 0.9rem',
          minWidth: '260px',
          flex: 1,
        }}>
          <Search size={16} color="var(--text-muted)" />
          <input
            type="text"
            placeholder="Search by diagnosis, body site, or Scan ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#ffffff',
              fontSize: '0.88rem',
              outline: 'none',
              width: '100%',
            }}
          />
        </div>

        {/* Risk Level Filter Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Filter size={14} color="var(--text-subtle)" style={{ marginRight: '4px' }} />
          {['all', 'low', 'moderate', 'high', 'uncertain'].map((risk) => (
            <button
              key={risk}
              onClick={() => setSelectedRiskFilter(risk)}
              style={{
                background: selectedRiskFilter === risk ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.05)',
                color: selectedRiskFilter === risk ? '#ffffff' : 'var(--text-muted)',
                border: 'none',
                padding: '0.4rem 0.8rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                textTransform: 'capitalize',
                transition: 'all 0.2s ease',
              }}
            >
              {risk}
            </button>
          ))}
        </div>
      </div>

      {/* History Items Grid */}
      {filteredHistory.length === 0 ? (
        <div className="glass-panel" style={{ padding: '4rem 2rem', textAlign: 'center' }}>
          <HistoryIcon size={48} color="var(--text-subtle)" style={{ marginBottom: '1rem' }} />
          <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>No Screening Records Found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            {searchTerm || selectedRiskFilter !== 'all' ? 'Try adjusting your search query or risk level filter.' : 'You have not performed any AI diagnostic scans yet.'}
          </p>
          <button onClick={onNewScreening} className="btn-primary" style={{ margin: '0 auto' }}>
            <PlusCircle size={16} /> Run Your First Scan
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {filteredHistory.map((item) => {
            const riskColor = getRiskColor(item.riskLevel);

            return (
              <div
                key={item.id}
                className="glass-card"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '1rem',
                  borderTop: `3px solid ${riskColor}`,
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600 }}>
                      ID: {item.id}
                    </span>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: riskColor,
                      textTransform: 'uppercase',
                      background: 'rgba(255, 255, 255, 0.05)',
                      padding: '0.15rem 0.5rem',
                      borderRadius: '4px',
                    }}>
                      {item.riskLevel} Risk
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <img
                      src={item.imageSrc}
                      alt={item.primaryPrediction}
                      style={{
                        width: '70px',
                        height: '70px',
                        borderRadius: 'var(--radius-md)',
                        objectFit: 'cover',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                      }}
                    />
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.2rem', color: 'var(--text-main)' }}>
                        {item.primaryPrediction}
                      </h4>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Site: {item.bodySite}
                      </p>
                      <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>
                        Confidence: {formatPercentage(item.confidenceScore)}
                      </span>
                    </div>
                  </div>

                  <div style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Calendar size={13} /> {formatDate(item.date)}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
                  <button
                    onClick={() => onSelectHistoryItem(item)}
                    className="btn-secondary"
                    style={{ flex: 1, padding: '0.5rem', fontSize: '0.8rem', justifyContent: 'center' }}
                  >
                    <Eye size={14} /> View Report
                  </button>
                  <button
                    onClick={() => onDeleteItem(item.id)}
                    style={{
                      background: 'rgba(244, 63, 94, 0.1)',
                      border: '1px solid rgba(244, 63, 94, 0.2)',
                      color: '#f43f5e',
                      padding: '0.5rem',
                      borderRadius: 'var(--radius-md)',
                      cursor: 'pointer',
                    }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
