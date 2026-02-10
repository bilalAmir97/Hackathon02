/**
 * useStreaming Hook
 *
 * Manages streaming response state with token buffering and callbacks.
 * Handles the streaming protocol and provides a clean interface for components.
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import { ToolCall, StreamingCallbacks } from '@/types/chat';

interface UseStreamingReturn {
  streamingMessage: string;
  isStreaming: boolean;
  toolCalls: ToolCall[];
  startStreaming: () => void;
  stopStreaming: () => void;
  appendToken: (token: string) => void;
  addToolCall: (toolCall: ToolCall) => void;
  reset: () => void;
}

/**
 * useStreaming hook for managing streaming response state
 */
export function useStreaming(): UseStreamingReturn {
  const [streamingMessage, setStreamingMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const bufferRef = useRef<string>('');

  /**
   * Start streaming
   */
  const startStreaming = useCallback(() => {
    setIsStreaming(true);
    setStreamingMessage('');
    setToolCalls([]);
    bufferRef.current = '';
  }, []);

  /**
   * Stop streaming
   */
  const stopStreaming = useCallback(() => {
    setIsStreaming(false);
  }, []);

  /**
   * Append token to streaming message
   */
  const appendToken = useCallback((token: string) => {
    bufferRef.current += token;
    setStreamingMessage(bufferRef.current);
  }, []);

  /**
   * Add tool call to list
   */
  const addToolCall = useCallback((toolCall: ToolCall) => {
    setToolCalls((prev) => {
      // Check if this tool call already exists (update case)
      const existingIndex = prev.findIndex(
        (tc) =>
          tc.tool_name === toolCall.tool_name &&
          tc.timestamp === toolCall.timestamp
      );

      if (existingIndex >= 0) {
        // Update existing tool call
        const updated = [...prev];
        updated[existingIndex] = toolCall;
        return updated;
      }

      // Add new tool call
      return [...prev, toolCall];
    });
  }, []);

  /**
   * Reset streaming state
   */
  const reset = useCallback(() => {
    setStreamingMessage('');
    setIsStreaming(false);
    setToolCalls([]);
    bufferRef.current = '';
  }, []);

  return {
    streamingMessage,
    isStreaming,
    toolCalls,
    startStreaming,
    stopStreaming,
    appendToken,
    addToolCall,
    reset,
  };
}
