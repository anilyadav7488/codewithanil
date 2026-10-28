import { describe, it, expect } from 'vitest';

describe('Frontend Core Suites', () => {
  it('validates text length constraints correctly', () => {
    const text = 'This is a sample sentence designed for testing text classification heuristics.';
    const words = text.trim().split(/\s+/).filter(Boolean).length;
    expect(words).toBeGreaterThan(5);
    expect(words).toBe(11);
  });

  it('correctly calculates calibration percentage bounds', () => {
    const aiScore = 0.884;
    const percentage = Math.round(aiScore * 100);
    expect(percentage).toBe(88);
    expect(percentage).toBeGreaterThanOrEqual(0);
    expect(percentage).toBeLessThanOrEqual(100);
  });

  it('determines classification boundary for inconclusive range', () => {
    const isMarginal = (score: number) => score >= 0.40 && score <= 0.60;
    expect(isMarginal(0.50)).toBe(true);
    expect(isMarginal(0.42)).toBe(true);
    expect(isMarginal(0.85)).toBe(false);
    expect(isMarginal(0.15)).toBe(false);
  });
});
