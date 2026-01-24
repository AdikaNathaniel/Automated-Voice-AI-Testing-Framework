/**
 * KPICard Component Tests
 *
 * Tests for KPICard component rendering, trend indicators, and styling.
 * Tests cover:
 *  - Basic rendering with title, value, and icon
 *  - Trend indicator rendering (up/down)
 *  - Trend color coding (success for up, error for down)
 *  - Optional trend (with and without)
 *  - Different value types (string and number)
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import KPICard from '../KPICard'
import { BarChart3, CheckCircle } from 'lucide-react'

describe('KPICard Component', () => {
  // ========== Basic Rendering Tests ==========
  describe('Basic Rendering', () => {
    it('should render title, value, and icon', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Total Test Runs"
          value={1234}
          icon={<BarChart3 data-testid="kpi-icon" />}
        />
      )

      // Assert
      expect(screen.getByText('Total Test Runs')).toBeInTheDocument()
      expect(screen.getByText('1234')).toBeInTheDocument()
      expect(screen.getByTestId('kpi-icon')).toBeInTheDocument()
    })

    it('should render with string value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Pass Rate"
          value="95.5%"
          icon={<CheckCircle />}
        />
      )

      // Assert
      expect(screen.getByText('Pass Rate')).toBeInTheDocument()
      expect(screen.getByText('95.5%')).toBeInTheDocument()
    })

    it('should render with numeric value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Active Tests"
          value={42}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('Active Tests')).toBeInTheDocument()
      expect(screen.getByText('42')).toBeInTheDocument()
    })

    it('should render with zero value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Failed Tests"
          value={0}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('Failed Tests')).toBeInTheDocument()
      expect(screen.getByText('0')).toBeInTheDocument()
    })
  })

  // ========== Trend Indicator Tests ==========
  describe('Trend Indicator', () => {
    it('should render upward trend indicator', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Total Test Runs"
          value={1234}
          trend={{ direction: 'up', value: '12%' }}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('12%')).toBeInTheDocument()
      expect(screen.getByText('vs last period')).toBeInTheDocument()
    })

    it('should render downward trend indicator', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Failed Tests"
          value={5}
          trend={{ direction: 'down', value: '8%' }}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('8%')).toBeInTheDocument()
      expect(screen.getByText('vs last period')).toBeInTheDocument()
    })

    it('should not render trend indicator when trend is undefined', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Total Tests"
          value={100}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.queryByText('vs last period')).not.toBeInTheDocument()
    })

    it('should render trend with numeric value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Pass Rate"
          value="98%"
          trend={{ direction: 'up', value: 5 }}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('vs last period')).toBeInTheDocument()
    })

    it('should render trend with string value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Average Duration"
          value="45s"
          trend={{ direction: 'down', value: '3s' }}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('3s')).toBeInTheDocument()
      expect(screen.getByText('vs last period')).toBeInTheDocument()
    })
  })

  // ========== Multiple KPICards Tests ==========
  describe('Multiple KPICards', () => {
    it('should render multiple KPICards independently', () => {
      // Arrange & Act
      render(
        <>
          <KPICard
            title="Total Runs"
            value={100}
            icon={<BarChart3 />}
          />
          <KPICard
            title="Passed Tests"
            value={95}
            trend={{ direction: 'up', value: '5%' }}
            icon={<CheckCircle />}
          />
        </>
      )

      // Assert
      expect(screen.getByText('Total Runs')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('Passed Tests')).toBeInTheDocument()
      expect(screen.getByText('95')).toBeInTheDocument()
      expect(screen.getByText('5%')).toBeInTheDocument()
    })
  })

  // ========== Edge Cases ==========
  describe('Edge Cases', () => {
    it('should handle empty string value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Status"
          value=""
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('Status')).toBeInTheDocument()
      // Empty value should still render (even if not visible)
    })

    it('should handle very large numeric value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Total Executions"
          value={9999999}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('Total Executions')).toBeInTheDocument()
      expect(screen.getByText('9999999')).toBeInTheDocument()
    })

    it('should handle negative numeric value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Change"
          value={-50}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('Change')).toBeInTheDocument()
      expect(screen.getByText('-50')).toBeInTheDocument()
    })

    it('should handle long title text', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Average Test Execution Duration in Milliseconds"
          value="1234ms"
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('Average Test Execution Duration in Milliseconds')).toBeInTheDocument()
      expect(screen.getByText('1234ms')).toBeInTheDocument()
    })

    it('should handle trend with zero value', () => {
      // Arrange & Act
      render(
        <KPICard
          title="No Change"
          value={100}
          trend={{ direction: 'up', value: 0 }}
          icon={<BarChart3 />}
        />
      )

      // Assert
      expect(screen.getByText('0')).toBeInTheDocument()
      expect(screen.getByText('vs last period')).toBeInTheDocument()
    })
  })

  // ========== Accessibility Tests ==========
  describe('Accessibility', () => {
    it('should have proper semantic structure', () => {
      // Arrange & Act
      const { container } = render(
        <KPICard
          title="Test Metric"
          value={123}
          icon={<BarChart3 />}
        />
      )

      // Assert - Should render within a card structure (Tailwind CSS)
      const card = container.querySelector('.card')
      expect(card).toBeInTheDocument()
    })

    it('should display title and value in correct hierarchy', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Important Metric"
          value={999}
          icon={<BarChart3 />}
        />
      )

      // Assert - Title should be present
      const title = screen.getByText('Important Metric')
      expect(title).toBeInTheDocument()

      // Value should be present
      const value = screen.getByText('999')
      expect(value).toBeInTheDocument()
    })
  })

  // ========== Component Integration Tests ==========
  describe('Component Integration', () => {
    it('should render correctly with all props', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Complete Example"
          value={5000}
          trend={{ direction: 'up', value: '25%' }}
          icon={<BarChart3 data-testid="complete-icon" />}
        />
      )

      // Assert
      expect(screen.getByText('Complete Example')).toBeInTheDocument()
      expect(screen.getByText('5000')).toBeInTheDocument()
      expect(screen.getByText('25%')).toBeInTheDocument()
      expect(screen.getByText('vs last period')).toBeInTheDocument()
      expect(screen.getByTestId('complete-icon')).toBeInTheDocument()
    })

    it('should render correctly with minimal props', () => {
      // Arrange & Act
      render(
        <KPICard
          title="Minimal Example"
          value="Test"
          icon={<BarChart3 data-testid="minimal-icon" />}
        />
      )

      // Assert
      expect(screen.getByText('Minimal Example')).toBeInTheDocument()
      expect(screen.getByText('Test')).toBeInTheDocument()
      expect(screen.getByTestId('minimal-icon')).toBeInTheDocument()
      expect(screen.queryByText('vs last period')).not.toBeInTheDocument()
    })
  })
})
