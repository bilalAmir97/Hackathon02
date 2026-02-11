/**
 * ToolCallIndicator Component
 *
 * Displays tool call execution with status indicators.
 * Shows tool name, status (pending/success/error), and results.
 */

'use client';

import { ToolCall } from '@/types/chat';

interface ToolCallIndicatorProps {
  toolCall: ToolCall;
}

/**
 * ToolCallIndicator component for displaying tool execution
 */
export function ToolCallIndicator({ toolCall }: ToolCallIndicatorProps) {
  const { tool_name, execution_status, input_parameters, output_result, error_message } = toolCall;

  // Status icon and color
  const getStatusDisplay = () => {
    switch (execution_status) {
      case 'pending':
        return {
          icon: (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600"></div>
          ),
          color: 'bg-blue-50 border-blue-200 text-blue-800',
          label: 'Executing...',
        };
      case 'success':
        return {
          icon: (
            <svg className="h-4 w-4 text-green-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M5 13l4 4L19 7" />
            </svg>
          ),
          color: 'bg-green-50 border-green-200 text-green-800',
          label: 'Completed',
        };
      case 'error':
        return {
          icon: (
            <svg className="h-4 w-4 text-red-600" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M6 18L18 6M6 6l12 12" />
            </svg>
          ),
          color: 'bg-red-50 border-red-200 text-red-800',
          label: 'Failed',
        };
      default:
        return {
          icon: null,
          color: 'bg-gray-50 border-gray-200 text-gray-800',
          label: 'Unknown',
        };
    }
  };

  const statusDisplay = getStatusDisplay();

  // Format tool name for display
  const formatToolName = (name: string) => {
    return name
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className={`my-2 rounded-xl border p-3 backdrop-blur-xl ${statusDisplay.color}`}>
      <div className="flex items-start space-x-2">
        <div className="mt-0.5">{statusDisplay.icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-semibold">
              {formatToolName(tool_name)}
            </span>
            <span className="text-xs opacity-75 font-medium">{statusDisplay.label}</span>
          </div>

          {/* Show input parameters for pending/success */}
          {(execution_status === 'pending' || execution_status === 'success') && input_parameters && Object.keys(input_parameters).length > 0 && (
            <div className="mt-2 text-xs opacity-80 space-y-1">
              {Object.entries(input_parameters).map(([key, value]) => (
                <div key={key} className="flex gap-1">
                  <span className="font-semibold">{key}:</span>{' '}
                  <span className="truncate">{typeof value === 'string' ? value : JSON.stringify(value)}</span>
                </div>
              ))}
            </div>
          )}

          {/* Show output result for success */}
          {execution_status === 'success' && output_result && (
            <div className="mt-2 text-xs">
              <div className="font-semibold mb-1">Result:</div>
              <div className="bg-black/10 rounded-lg p-2 font-mono text-xs overflow-x-auto">
                {typeof output_result === 'string'
                  ? output_result
                  : JSON.stringify(output_result, null, 2)}
              </div>
            </div>
          )}

          {/* Show error message for errors */}
          {execution_status === 'error' && error_message && (
            <div className="mt-2 text-xs">
              <span className="font-semibold">Error:</span> {error_message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
