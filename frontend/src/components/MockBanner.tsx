import React from 'react'

interface MockBannerProps {
  visible?: boolean
}

export const MockBanner: React.FC<MockBannerProps> = ({ visible = true }) => {
  if (!visible) return null

  return (
    <div
      role="status"
      aria-live="polite"
      className="cercos-mock-banner"
      style={{
        backgroundColor: '#fef3c7',
        color: '#92400e',
        borderBottom: '1px solid #fde68a',
        padding: '6px 16px',
        fontSize: '13px',
        fontWeight: 600,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        zIndex: 1000,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span
          style={{
            display: 'inline-block',
            backgroundColor: '#d97706',
            color: '#fff',
            borderRadius: '4px',
            padding: '2px 6px',
            fontSize: '11px',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          Mock data
        </span>
        <span>Synthetic mode active — mock API handlers responding</span>
      </div>
      <span style={{ fontSize: '11px', color: '#b45309' }}>
        EPICS Phase-I • Bhopal Region
      </span>
    </div>
  )
}
