/**
 * WaveformVisualization Component
 *
 * Animated SVG waveform visualization for the hero section.
 * Includes floating metric badges around the waveform.
 */

import React from 'react';
import { Brain, Globe, GitBranch } from 'lucide-react';

interface FloatingMetricProps {
  value: string;
  label: string;
  icon: React.ReactNode;
  position: 'top-right' | 'bottom-left' | 'bottom-right';
  delay?: number;
}

const FloatingMetric: React.FC<FloatingMetricProps> = ({
  value,
  label,
  icon,
  position,
  delay = 0,
}) => {
  const positionClasses = {
    'top-right': 'top-4 right-4 lg:top-8 lg:right-0',
    'bottom-left': 'bottom-4 left-4 lg:bottom-8 lg:left-0',
    'bottom-right': 'bottom-4 right-4 lg:bottom-16 lg:right-4',
  };

  return (
    <div
      className={`
        absolute ${positionClasses[position]}
        animate-fade-up animate-float
        bg-[var(--color-surface-raised)]
        rounded-xl shadow-lg border border-[var(--color-border-default)]
        px-4 py-3 flex items-center gap-3
      `}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#2A6B6E] to-[#11484D] flex items-center justify-center text-white">
        {icon}
      </div>
      <div>
        <div className="text-lg font-bold text-[var(--color-content-primary)]">
          {value}
        </div>
        <div className="text-xs text-[var(--color-content-muted)]">
          {label}
        </div>
      </div>
    </div>
  );
};

interface WaveformVisualizationProps {
  className?: string;
  showMetrics?: boolean;
}

const WaveformVisualization: React.FC<WaveformVisualizationProps> = ({
  className = '',
  showMetrics = true,
}) => {
  // Waveform bar configuration - 9 bars with varying heights
  const bars = [
    { height: 30, delay: 0 },
    { height: 50, delay: 100 },
    { height: 70, delay: 200 },
    { height: 90, delay: 300 },
    { height: 100, delay: 400 },
    { height: 90, delay: 500 },
    { height: 70, delay: 600 },
    { height: 50, delay: 700 },
    { height: 30, delay: 800 },
  ];

  return (
    <div className={`relative ${className}`}>
      {/* Main Waveform Container */}
      <div className="relative w-full max-w-lg mx-auto aspect-square flex items-center justify-center">
        {/* Background glow effect */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#2A6B6E]/20 via-transparent to-[#11484D]/10 rounded-full blur-3xl" />

        {/* Waveform SVG */}
        <svg
          viewBox="0 0 200 120"
          className="w-full h-auto max-h-72 animate-scale-in"
          style={{ animationDelay: '200ms' }}
        >
          <defs>
            {/* Gradient for bars */}
            <linearGradient id="waveGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#3D8285" />
              <stop offset="100%" stopColor="#11484D" />
            </linearGradient>
            {/* Glow filter */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="2" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Animated waveform bars */}
          <g filter="url(#glow)">
            {bars.map((bar, index) => {
              const x = 20 + index * 20;
              const baseY = 60;
              const barHeight = bar.height * 0.5;

              return (
                <rect
                  key={index}
                  x={x}
                  y={baseY - barHeight / 2}
                  width="8"
                  height={barHeight}
                  rx="4"
                  fill="url(#waveGradient)"
                  className="animate-wave-bar"
                  style={{
                    animationDelay: `${bar.delay}ms`,
                    transformOrigin: `${x + 4}px ${baseY}px`,
                  }}
                />
              );
            })}
          </g>

          {/* Connection line */}
          <path
            d="M20 60 Q 100 40, 180 60"
            fill="none"
            stroke="#2A6B6E"
            strokeWidth="1"
            strokeDasharray="4 4"
            opacity="0.3"
          />
        </svg>
      </div>

      {/* Floating Metrics */}
      {showMetrics && (
        <>
          <FloatingMetric
            value="AI+Human"
            label="Validation"
            icon={<Brain className="w-5 h-5" />}
            position="top-right"
            delay={800}
          />
          <FloatingMetric
            value="8+"
            label="Languages"
            icon={<Globe className="w-5 h-5" />}
            position="bottom-left"
            delay={1000}
          />
          <FloatingMetric
            value="CI/CD"
            label="Ready"
            icon={<GitBranch className="w-5 h-5" />}
            position="bottom-right"
            delay={1200}
          />
        </>
      )}
    </div>
  );
};

export default WaveformVisualization;
