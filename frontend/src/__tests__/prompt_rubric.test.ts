import { describe, it, expect } from 'vitest';

describe('Prompt Rubric Dimension Scoring', () => {
  it('penalizes vague short prompts', () => {
    const prompt = 'write code fast';
    const hasRole = /you are|act as/i.test(prompt);
    const hasFormat = /json|markdown|table|list/i.test(prompt);
    const hasConstraints = /do not|limit|maximum|must/i.test(prompt);
    
    expect(hasRole).toBe(false);
    expect(hasFormat).toBe(false);
    expect(hasConstraints).toBe(false);
    expect(prompt.split(' ').length).toBeLessThan(5);
  });

  it('rewards comprehensive engineering prompts', () => {
    const prompt = 'You are a principal engineer. Output a Python script formatted in Markdown. Do not use external libraries.';
    const hasRole = /you are|act as/i.test(prompt);
    const hasFormat = /json|markdown|table|list/i.test(prompt);
    const hasConstraints = /do not|limit|maximum|must/i.test(prompt);

    expect(hasRole).toBe(true);
    expect(hasFormat).toBe(true);
    expect(hasConstraints).toBe(true);
  });
});
