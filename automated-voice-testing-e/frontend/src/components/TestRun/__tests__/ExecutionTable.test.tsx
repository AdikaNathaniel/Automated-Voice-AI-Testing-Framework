/**
 * ExecutionTable Component Tests
 *
 * Tests for ExecutionTable component rendering, sorting, and data display.
 * Tests cover:
 *  - Basic rendering with execution data
 *  - Sorting functionality (by name, language, status, confidence, duration)
 *  - Status color coding
 *  - Confidence color coding
 *  - Empty state
 *  - Edge cases (missing optional fields, undefined values)
 */

import { describe, it, expect } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ExecutionTable, { TestExecution } from '../ExecutionTable'

describe('ExecutionTable Component', () => {
  // Helper function to create mock executions
  const createMockExecution = (overrides?: Partial<TestExecution>): TestExecution => ({
    id: 1,
    name: 'Test Case 1',
    language: 'en-US',
    status: 'passed',
    confidence: 95,
    duration: 12.5,
    ...overrides,
  })

  // ========== Basic Rendering Tests ==========
  describe('Basic Rendering', () => {
    it('should render table headers', () => {
      // Arrange
      const executions: TestExecution[] = []

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('Test Name')).toBeInTheDocument()
      expect(screen.getByText('Language')).toBeInTheDocument()
      expect(screen.getByText('Status')).toBeInTheDocument()
      expect(screen.getByText('Confidence')).toBeInTheDocument()
      expect(screen.getByText('Time')).toBeInTheDocument()
    })

    it('should render execution data', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({
          id: 1,
          name: 'Login Test',
          language: 'en-US',
          status: 'passed',
          confidence: 95,
          duration: 10.5,
        }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('Login Test')).toBeInTheDocument()
      expect(screen.getByText('en-US')).toBeInTheDocument()
      expect(screen.getByText('passed')).toBeInTheDocument()
      expect(screen.getByText('95%')).toBeInTheDocument()
      expect(screen.getByText('10.5s')).toBeInTheDocument()
    })

    it('should render multiple executions', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, name: 'Test 1', status: 'passed' }),
        createMockExecution({ id: 2, name: 'Test 2', status: 'failed' }),
        createMockExecution({ id: 3, name: 'Test 3', status: 'running' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('Test 1')).toBeInTheDocument()
      expect(screen.getByText('Test 2')).toBeInTheDocument()
      expect(screen.getByText('Test 3')).toBeInTheDocument()
    })

    it('should render empty table with no executions', () => {
      // Arrange
      const executions: TestExecution[] = []

      // Act
      const { container } = render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('Test Name')).toBeInTheDocument()
      // Table body should be empty (no data rows)
      const tableBody = container.querySelector('tbody')
      expect(tableBody).toBeInTheDocument()
      expect(tableBody?.children.length).toBe(0)
    })
  })

  // ========== Status Display Tests ==========
  describe('Status Display', () => {
    it('should display passed status', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ status: 'passed' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('passed')).toBeInTheDocument()
    })

    it('should display failed status', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ status: 'failed' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('failed')).toBeInTheDocument()
    })

    it('should display running status', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ status: 'running' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('running')).toBeInTheDocument()
    })

    it('should display pending status', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ status: 'pending' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('pending')).toBeInTheDocument()
    })

    it('should display all different statuses', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, status: 'passed' }),
        createMockExecution({ id: 2, status: 'failed' }),
        createMockExecution({ id: 3, status: 'running' }),
        createMockExecution({ id: 4, status: 'pending' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('passed')).toBeInTheDocument()
      expect(screen.getByText('failed')).toBeInTheDocument()
      expect(screen.getByText('running')).toBeInTheDocument()
      expect(screen.getByText('pending')).toBeInTheDocument()
    })
  })

  // ========== Confidence Display Tests ==========
  describe('Confidence Display', () => {
    it('should display confidence percentage', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ confidence: 85 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('85%')).toBeInTheDocument()
    })

    it('should display dash for missing confidence', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ confidence: undefined }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      const cells = screen.getAllByRole('cell')
      const confidenceCell = cells.find(cell => cell.textContent === '-')
      expect(confidenceCell).toBeInTheDocument()
    })

    it('should display zero confidence', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ confidence: 0 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('0%')).toBeInTheDocument()
    })

    it('should display 100% confidence', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ confidence: 100 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('100%')).toBeInTheDocument()
    })
  })

  // ========== Duration Display Tests ==========
  describe('Duration Display', () => {
    it('should display duration in seconds', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ duration: 15.7 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('15.7s')).toBeInTheDocument()
    })

    it('should display dash for missing duration', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ duration: undefined }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      const cells = screen.getAllByRole('cell')
      const durationCells = cells.filter(cell => cell.textContent === '-')
      expect(durationCells.length).toBeGreaterThan(0)
    })

    it('should display zero duration', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ duration: 0 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('0s')).toBeInTheDocument()
    })

    it('should display large duration', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ duration: 999.99 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('999.99s')).toBeInTheDocument()
    })
  })

  // ========== Sorting Tests ==========
  describe('Sorting Functionality', () => {
    it('should sort by name ascending', async () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, name: 'Zebra Test' }),
        createMockExecution({ id: 2, name: 'Alpha Test' }),
        createMockExecution({ id: 3, name: 'Beta Test' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert - Should be sorted by name ascending by default
      const rows = screen.getAllByRole('row')
      // Skip header row (index 0), check data rows
      expect(within(rows[1]).getByText('Alpha Test')).toBeInTheDocument()
      expect(within(rows[2]).getByText('Beta Test')).toBeInTheDocument()
      expect(within(rows[3]).getByText('Zebra Test')).toBeInTheDocument()
    })

    it('should toggle sort order when clicking same column', async () => {
      // Arrange
      const user = userEvent.setup()
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, name: 'Alpha Test' }),
        createMockExecution({ id: 2, name: 'Beta Test' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)
      const nameHeader = screen.getByText('Test Name')

      // Click to sort descending
      await user.click(nameHeader)

      // Assert - Should be sorted descending
      const rows = screen.getAllByRole('row')
      expect(within(rows[1]).getByText('Beta Test')).toBeInTheDocument()
      expect(within(rows[2]).getByText('Alpha Test')).toBeInTheDocument()
    })

    it('should sort by language', async () => {
      // Arrange
      const user = userEvent.setup()
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, name: 'Test 1', language: 'es-ES' }),
        createMockExecution({ id: 2, name: 'Test 2', language: 'en-US' }),
        createMockExecution({ id: 3, name: 'Test 3', language: 'fr-FR' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Default sort is by name, click language to sort by language
      const languageHeader = screen.getByText('Language')
      await user.click(languageHeader)

      // Assert
      const rows = screen.getAllByRole('row')
      expect(within(rows[1]).getByText('en-US')).toBeInTheDocument()
      expect(within(rows[2]).getByText('es-ES')).toBeInTheDocument()
      expect(within(rows[3]).getByText('fr-FR')).toBeInTheDocument()
    })

    it('should sort by confidence', async () => {
      // Arrange
      const user = userEvent.setup()
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, name: 'Test 1', confidence: 50 }),
        createMockExecution({ id: 2, name: 'Test 2', confidence: 90 }),
        createMockExecution({ id: 3, name: 'Test 3', confidence: 70 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      const confidenceHeader = screen.getByText('Confidence')
      await user.click(confidenceHeader)

      // Assert
      const rows = screen.getAllByRole('row')
      expect(within(rows[1]).getByText('50%')).toBeInTheDocument()
      expect(within(rows[2]).getByText('70%')).toBeInTheDocument()
      expect(within(rows[3]).getByText('90%')).toBeInTheDocument()
    })

    it('should sort by duration', async () => {
      // Arrange
      const user = userEvent.setup()
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, name: 'Test 1', duration: 30 }),
        createMockExecution({ id: 2, name: 'Test 2', duration: 10 }),
        createMockExecution({ id: 3, name: 'Test 3', duration: 20 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      const timeHeader = screen.getByText('Time')
      await user.click(timeHeader)

      // Assert
      const rows = screen.getAllByRole('row')
      expect(within(rows[1]).getByText('10s')).toBeInTheDocument()
      expect(within(rows[2]).getByText('20s')).toBeInTheDocument()
      expect(within(rows[3]).getByText('30s')).toBeInTheDocument()
    })

    it('should handle sorting with undefined values', async () => {
      // Arrange
      const user = userEvent.setup()
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, name: 'A Test', confidence: 80 }),
        createMockExecution({ id: 2, name: 'B Test', confidence: undefined }),
        createMockExecution({ id: 3, name: 'C Test', confidence: 60 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      const confidenceHeader = screen.getByText('Confidence')
      await user.click(confidenceHeader)

      // Assert - Should not crash and should render all rows
      const rows = screen.getAllByRole('row')
      // Should have header row + 3 data rows
      expect(rows).toHaveLength(4)

      // All test names should still be visible
      expect(screen.getByText('A Test')).toBeInTheDocument()
      expect(screen.getByText('B Test')).toBeInTheDocument()
      expect(screen.getByText('C Test')).toBeInTheDocument()
    })
  })

  // ========== Language Display Tests ==========
  describe('Language Display', () => {
    it('should display different languages', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ id: 1, language: 'en-US' }),
        createMockExecution({ id: 2, language: 'es-ES' }),
        createMockExecution({ id: 3, language: 'fr-FR' }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('en-US')).toBeInTheDocument()
      expect(screen.getByText('es-ES')).toBeInTheDocument()
      expect(screen.getByText('fr-FR')).toBeInTheDocument()
    })
  })

  // ========== Edge Cases ==========
  describe('Edge Cases', () => {
    it('should handle execution with all optional fields missing', () => {
      // Arrange
      const executions: TestExecution[] = [
        {
          id: 1,
          name: 'Test Case',
          language: 'en-US',
          status: 'pending',
          confidence: undefined,
          duration: undefined,
        },
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('Test Case')).toBeInTheDocument()
      expect(screen.getByText('en-US')).toBeInTheDocument()
      expect(screen.getByText('pending')).toBeInTheDocument()
      const cells = screen.getAllByRole('cell')
      const dashCells = cells.filter(cell => cell.textContent === '-')
      expect(dashCells.length).toBeGreaterThanOrEqual(2) // At least 2 dash cells for confidence and duration
    })

    it('should handle very long test names', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({
          name: 'This is a very long test case name that might need to be truncated or wrapped',
        }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('This is a very long test case name that might need to be truncated or wrapped')).toBeInTheDocument()
    })

    it('should handle decimal confidence values', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ confidence: 85.5 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('85.5%')).toBeInTheDocument()
    })

    it('should handle very small duration values', () => {
      // Arrange
      const executions: TestExecution[] = [
        createMockExecution({ duration: 0.01 }),
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('0.01s')).toBeInTheDocument()
    })
  })

  // ========== Integration Tests ==========
  describe('Integration', () => {
    it('should render complete execution data correctly', () => {
      // Arrange
      const executions: TestExecution[] = [
        {
          id: 1,
          name: 'Login Flow Test',
          language: 'en-US',
          status: 'passed',
          confidence: 95,
          duration: 12.5,
        },
        {
          id: 2,
          name: 'Checkout Test',
          language: 'es-ES',
          status: 'failed',
          confidence: 45,
          duration: 8.3,
        },
        {
          id: 3,
          name: 'Search Test',
          language: 'fr-FR',
          status: 'running',
          confidence: undefined,
          duration: undefined,
        },
      ]

      // Act
      render(<ExecutionTable executions={executions} />)

      // Assert
      expect(screen.getByText('Login Flow Test')).toBeInTheDocument()
      expect(screen.getByText('Checkout Test')).toBeInTheDocument()
      expect(screen.getByText('Search Test')).toBeInTheDocument()
      expect(screen.getByText('95%')).toBeInTheDocument()
      expect(screen.getByText('45%')).toBeInTheDocument()
      expect(screen.getByText('12.5s')).toBeInTheDocument()
      expect(screen.getByText('8.3s')).toBeInTheDocument()
    })
  })
})
