import { Logger } from '@aws-lambda-powertools/logger';

const logger = new Logger({ serviceName: 'chat-api-ts' });

export function reportError(
  message: string,
  error?: unknown,
  context: Record<string, unknown> = {},
): void {
  logger.error(message, { error, ...context });
  // TODO: Once Sentry is added to this service, also forward here via
  // Sentry.captureException(error, { extra: { message, ...context } }).
}
