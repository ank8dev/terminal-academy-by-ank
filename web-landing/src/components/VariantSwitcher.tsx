import React from 'react';

interface VariantSwitcherProps {
  activeVariant: number;
  setActiveVariant: (variant: number) => void;
}

export const VariantSwitcher: React.FC<VariantSwitcherProps> = ({
  activeVariant,
  setActiveVariant,
}) => {
  const variants = [
    { id: 1, name: 'V1: Classic Redux' },
    { id: 2, name: 'V2: Workspace Simulator' },
    { id: 3, name: 'V3: Playground & Docs' },
    { id: 4, name: 'V4: Network Topology' },
    { id: 5, name: 'V5: Bento Matrix' },
  ];

  return (
    <div className="variant-switcher-bar">
      <div className="switcher-title">Academy Prototypes</div>
      <div className="switcher-buttons">
        {variants.map(v => (
          <button
            key={v.id}
            className={`switcher-btn ${activeVariant === v.id ? 'active' : ''}`}
            onClick={() => setActiveVariant(v.id)}
          >
            {v.name}
          </button>
        ))}
      </div>
    </div>
  );
};
