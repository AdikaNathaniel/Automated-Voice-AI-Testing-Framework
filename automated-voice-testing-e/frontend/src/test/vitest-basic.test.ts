/**
 * Basic Vitest Verification Tests
 *
 * Simple tests that verify Vitest is working without any dependencies
 * on React, Redux, or other complex libraries.
 */

import { describe, it, expect, vi } from 'vitest'

describe('Vitest Basic Setup', () => {
  it('should run a simple test', () => {
    expect(true).toBe(true)
  })

  it('should perform basic assertions', () => {
    const value = 'test'
    const number = 42

    expect(value).toBe('test')
    expect(number).toEqual(42)
    expect([1, 2, 3]).toHaveLength(3)
  })

  it('should support async tests', async () => {
    const result = await Promise.resolve('async')
    expect(result).toBe('async')
  })

  it('should support mocking', () => {
    const mockFn = vi.fn()
    mockFn('test')

    expect(mockFn).toHaveBeenCalled()
    expect(mockFn).toHaveBeenCalledWith('test')
  })

  it('should support object matchers', () => {
    const obj = { a: 1, b: 2 }
    expect(obj).toEqual({ a: 1, b: 2 })
    expect(obj).toHaveProperty('a')
    expect(obj).toHaveProperty('b', 2)
  })

  it('should support array matchers', () => {
    const arr = [1, 2, 3]
    expect(arr).toContain(2)
    expect(arr).toHaveLength(3)
    expect(arr).toEqual([1, 2, 3])
  })

  it('should support truthiness matchers', () => {
    expect(null).toBeNull()
    expect(undefined).toBeUndefined()
    expect(true).toBeTruthy()
    expect(false).toBeFalsy()
  })

  it('should support number comparisons', () => {
    expect(10).toBeGreaterThan(5)
    expect(5).toBeLessThan(10)
    expect(10).toBeGreaterThanOrEqual(10)
    expect(5).toBeLessThanOrEqual(5)
  })

  it('should support string matchers', () => {
    expect('Hello World').toMatch(/World/)
    expect('test@example.com').toMatch(/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/)
  })

  it('should support exception testing', () => {
    const throwError = () => {
      throw new Error('Test error')
    }

    expect(throwError).toThrow()
    expect(throwError).toThrow('Test error')
    expect(throwError).toThrow(Error)
  })
})
