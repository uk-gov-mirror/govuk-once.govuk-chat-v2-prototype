import { beforeEach, describe, expect, it, vi } from 'vitest';

const error = vi.fn();

vi.mock('@aws-lambda-powertools/logger', () => ({
  Logger: vi.fn().mockImplementation(function () {
    return { error };
  }),
}));

describe('reportError', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('logs the message with the error and any additional context', async () => {
    const { reportError } = await import('./report-error.ts');
    const cause = new Error('boom');

    reportError('Something failed', cause, { threadId: 'thread-1' });

    expect(error).toHaveBeenCalledWith('Something failed', {
      error: cause,
      threadId: 'thread-1',
    });
  });

  it('defaults context to an empty object when none is given', async () => {
    const { reportError } = await import('./report-error.ts');
    const cause = new Error('boom');

    reportError('Something failed', cause);

    expect(error).toHaveBeenCalledWith('Something failed', { error: cause });
  });

  it('supports omitting the error when there is no underlying exception', async () => {
    const { reportError } = await import('./report-error.ts');

    reportError('Something unexpected happened', undefined, {
      threadId: 'thread-1',
    });

    expect(error).toHaveBeenCalledWith('Something unexpected happened', {
      error: undefined,
      threadId: 'thread-1',
    });
  });
});
