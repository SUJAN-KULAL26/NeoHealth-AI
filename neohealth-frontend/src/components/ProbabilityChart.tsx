import React, { useState } from 'react';
import { BarChart3, Info, ChevronDown, ChevronUp } from 'lucide-react';
import type { ClassProbability } from '../types/screening';
import { formatPercentage, getRiskColor } from '../utils/validation';

interface ProbabilityChartProps {
  probabilities: ClassProbability[];
}

export const ProbabilityChart: React.FC<ProbabilityChartProps> = ({ probabilities }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  // Sort descending by probability
  const sortedProbabilities = [...probabilities].sort((a, b) => b.probability - a.probability);

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <BarChart3 size={22} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '1.3rem', fontWeight: 800 }}>6-Class Probability Distribution</h3>
        </div>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', background: 'rgba(255, 255, 255, 0.05)', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
          Softmax Neural Outputs
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {sortedProbabilities.map((item, index) => {
          const color = getRiskColor(item.riskLevel);
          const isExpanded = expandedId === item.id;
          const isTopRanked = index === 0;

          return (
            <div
              key={item.id}
              style={{
                background: isTopRanked ? 'rgba(6, 182, 212, 0.08)' : 'rgba(13, 21, 39, 0.6)',
                border: isTopRanked ? '1px solid rgba(6, 182, 212, 0.4)' : '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: 'var(--radius-md)',
                padding: '1.1rem',
                transition: 'all 0.2s ease',
              }}
            >
              <div
                onClick={() => toggleExpand(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  marginBottom: '0.65rem',
                  gap: '0.5rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 800,
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    background: isTopRanked ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.08)',
                    color: isTopRanked ? '#ffffff' : 'var(--text-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    #{index + 1}
                  </span>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                        {item.label}
                      </span>
                      {isTopRanked && (
                        <span style={{
                          fontSize: '0.68rem',
                          background: 'rgba(6, 182, 212, 0.2)',
                          color: '#38bdf8',
                          padding: '0.1rem 0.45rem',
                          borderRadius: '999px',
                          fontWeight: 700,
                        }}>
                          PRIMARY
                        </span>
                      )}
                    </div>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-subtle)' }}>
                      {item.category}
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <span style={{ fontSize: '1.2rem', fontWeight: 800, color: color }}>
                    {formatPercentage(item.probability)}
                  </span>
                  {isExpanded ? <ChevronUp size={16} color="var(--text-muted)" /> : <ChevronDown size={16} color="var(--text-muted)" />}
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{
                width: '100%',
                height: '8px',
                background: 'rgba(255, 255, 255, 0.06)',
                borderRadius: '999px',
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  width: `${Math.max(2, item.probability)}%`,
                  background: isTopRanked
                    ? 'linear-gradient(90deg, #38bdf8 0%, #06b6d4 100%)'
                    : color,
                  borderRadius: '999px',
                  transition: 'width 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
                  boxShadow: isTopRanked ? '0 0 10px rgba(6, 182, 212, 0.6)' : 'none',
                }} />
              </div>

              {/* Collapsible Details */}
              {isExpanded && (
                <div style={{
                  marginTop: '0.85rem',
                  paddingTop: '0.85rem',
                  borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                  fontSize: '0.85rem',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.6rem',
                  lineHeight: 1.45,
                }}>
                  <Info size={16} color="var(--accent-cyan)" style={{ marginTop: '2px', flexShrink: 0 }} />
                  <p>{item.description}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
