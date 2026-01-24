/**
 * PipelineView component tests.
 */

import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

import PipelineView from '../PipelineView';

const baseStages = [
  {
    id: 'checkout',
    name: 'Checkout',
    status: 'success' as const,
    durationSeconds: 35,
  },
  {
    id: 'build',
    name: 'Build',
    status: 'running' as const,
    durationSeconds: 120,
  },
  {
    id: 'test',
    name: 'Tests',
    status: 'pending' as const,
    durationSeconds: null,
  },
];

describe('PipelineView', () => {
  it('renders stages with status badges and duration', () => {
    render(<PipelineView stages={baseStages} />);

    expect(screen.getByText('Checkout')).toBeInTheDocument();
    expect(
      screen.getByText((content) => content.includes('Duration: 35s'))
    ).toBeInTheDocument();
    expect(screen.getByTestId('pipeline-stage-status-checkout')).toHaveTextContent(/success/i);

    expect(screen.getByText('Build')).toBeInTheDocument();
    expect(
      screen.getByText((content) => content.includes('Duration: 2m 0s'))
    ).toBeInTheDocument();
    expect(screen.getByTestId('pipeline-stage-status-build')).toHaveTextContent(/running/i);
  });

  it('renders a message when no stages are provided', () => {
    render(<PipelineView stages={[]} />);

    expect(screen.getByText(/No pipeline stages available/i)).toBeInTheDocument();
  });

  it('shows error banner when provided', () => {
    render(<PipelineView stages={baseStages} error="Failed to load pipeline" />);

    expect(screen.getByText(/Failed to load pipeline/i)).toBeInTheDocument();
  });
});
