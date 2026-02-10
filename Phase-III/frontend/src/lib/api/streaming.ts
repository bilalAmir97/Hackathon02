/**
 * Streaming utilities for handling NDJSON streaming responses
 *
 * Provides utilities for processing ReadableStream responses with
 * NDJSON (Newline Delimited JSON) format from the backend.
 */

import {
  StreamChunk,
  StreamingCallbacks,
  StreamInterruptedError,
  ChatError,
} from '@/types/chat';

/**
 * Process a streaming response from the backend
 *
 * @param response - Fetch Response object with streaming body
 * @param callbacks - Callbacks for handling different chunk types
 * @throws StreamInterruptedError if stream is interrupted
 * @throws ChatError if parsing fails
 */
export async function processStreamingResponse(
  response: Response,
  callbacks: StreamingCallbacks
): Promise<void> {
  const reader = response.body?.getReader();

  if (!reader) {
    throw new ChatError('Response body is not readable', 'NO_READER');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        // Process any remaining data in buffer
        if (buffer.trim()) {
          processLine(buffer, callbacks);
        }
        break;
      }

      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete lines (NDJSON format)
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.trim()) {
          processLine(line, callbacks);
        }
      }
    }
  } catch (error) {
    // Stream was interrupted
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new StreamInterruptedError('Stream was cancelled');
    }

    // Re-throw ChatError as-is
    if (error instanceof ChatError) {
      throw error;
    }

    // Wrap other errors
    throw new StreamInterruptedError(
      error instanceof Error ? error.message : 'Stream processing failed'
    );
  } finally {
    // Always release the reader
    reader.releaseLock();
  }
}

/**
 * Process a single line of NDJSON
 *
 * @param line - Single line of JSON
 * @param callbacks - Callbacks for handling different chunk types
 */
function processLine(line: string, callbacks: StreamingCallbacks): void {
  try {
    const chunk = JSON.parse(line) as StreamChunk;

    switch (chunk.type) {
      case 'token':
        callbacks.onToken(chunk.content);
        break;

      case 'tool_call':
        callbacks.onToolCall(chunk.data);
        break;

      case 'done':
        callbacks.onComplete(chunk.conversation_id, chunk.message_id);
        break;

      case 'error':
        callbacks.onError(new ChatError(chunk.message, chunk.code));
        break;

      default:
        console.warn('Unknown chunk type:', chunk);
    }
  } catch (parseError) {
    console.error('Failed to parse NDJSON line:', line, parseError);
    // Don't throw - continue processing other lines
  }
}

/**
 * Create an AbortController for cancelling streams
 *
 * @returns AbortController instance
 */
export function createStreamController(): AbortController {
  return new AbortController();
}

/**
 * Batch tokens for more efficient rendering
 *
 * Instead of rendering every single token, batch them together
 * to reduce React re-renders and improve performance.
 *
 * @param onToken - Original token callback
 * @param batchSize - Number of tokens to batch (default: 5)
 * @param flushInterval - Max time to wait before flushing (ms, default: 50)
 * @returns Batched token callback and flush function
 */
export function createBatchedTokenHandler(
  onToken: (tokens: string) => void,
  batchSize: number = 5,
  flushInterval: number = 50
): {
  handleToken: (token: string) => void;
  flush: () => void;
} {
  let buffer: string[] = [];
  let timeoutId: NodeJS.Timeout | null = null;

  const flush = () => {
    if (buffer.length > 0) {
      onToken(buffer.join(''));
      buffer = [];
    }
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  const handleToken = (token: string) => {
    buffer.push(token);

    // Flush if batch size reached
    if (buffer.length >= batchSize) {
      flush();
      return;
    }

    // Schedule flush if not already scheduled
    if (!timeoutId) {
      timeoutId = setTimeout(flush, flushInterval);
    }
  };

  return { handleToken, flush };
}

/**
 * Stream with retry logic
 *
 * Attempts to process a stream with automatic retry on failure.
 *
 * @param fetchFn - Function that returns a fetch Response
 * @param callbacks - Streaming callbacks
 * @param maxRetries - Maximum number of retry attempts (default: 3)
 * @param retryDelay - Delay between retries in ms (default: 1000)
 */
export async function streamWithRetry(
  fetchFn: () => Promise<Response>,
  callbacks: StreamingCallbacks,
  maxRetries: number = 3,
  retryDelay: number = 1000
): Promise<void> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetchFn();
      await processStreamingResponse(response, callbacks);
      return; // Success
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error');

      // Don't retry on authentication errors
      if (error instanceof ChatError && error.statusCode === 401) {
        throw error;
      }

      // Don't retry if this was the last attempt
      if (attempt === maxRetries) {
        break;
      }

      // Wait before retrying
      await new Promise((resolve) => setTimeout(resolve, retryDelay));
    }
  }

  // All retries failed
  throw new StreamInterruptedError(
    `Stream failed after ${maxRetries + 1} attempts: ${lastError?.message}`
  );
}

/**
 * Validate streaming response before processing
 *
 * @param response - Fetch Response object
 * @throws ChatError if response is invalid
 */
export function validateStreamingResponse(response: Response): void {
  if (!response.ok) {
    throw new ChatError(
      `HTTP ${response.status}: ${response.statusText}`,
      'HTTP_ERROR',
      response.status
    );
  }

  const contentType = response.headers.get('content-type');
  if (contentType && !contentType.includes('application/x-ndjson')) {
    console.warn(
      `Expected content-type 'application/x-ndjson', got '${contentType}'`
    );
  }

  if (!response.body) {
    throw new ChatError('Response has no body', 'NO_BODY');
  }
}
