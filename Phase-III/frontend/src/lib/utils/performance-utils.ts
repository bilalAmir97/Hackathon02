/**
 * Performance utilities for measuring and monitoring application performance
 */

/**
 * FPS Counter utility to measure frames per second
 */
export class FPSCounter {
  private frameCount: number;
  private lastTime: number;
  private fps: number;
  private callback: (fps: number) => void;

  constructor(callback: (fps: number) => void) {
    this.frameCount = 0;
    this.lastTime = performance.now();
    this.fps = 0;
    this.callback = callback;
  }

  /**
   * Call this method on each frame to measure FPS
   */
  tick(): void {
    this.frameCount++;
    const currentTime = performance.now();

    // Calculate FPS every second
    if (currentTime >= this.lastTime + 1000) {
      this.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime));
      this.callback(this.fps);

      // Reset counters
      this.frameCount = 0;
      this.lastTime = currentTime;
    }
  }

  /**
   * Get the current FPS
   */
  getCurrentFPS(): number {
    return this.fps;
  }

  /**
   * Start monitoring FPS using requestAnimationFrame
   */
  start(): () => void {
    let animationFrameId: number;

    const update = () => {
      this.tick();
      animationFrameId = requestAnimationFrame(update);
    };

    animationFrameId = requestAnimationFrame(update);

    // Return a function to stop monitoring
    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }
}

/**
 * Measure function execution time
 */
export const measureFunctionTime = async <T>(
  fn: () => T | Promise<T>,
  label: string = 'Function execution'
): Promise<{ result: T; duration: number }> => {
  const start = performance.now();
  const result = await Promise.resolve(fn());
  const end = performance.now();
  const duration = end - start;

  console.log(`${label}: ${duration.toFixed(2)}ms`);
  return { result, duration };
};

/**
 * Monitor memory usage if available
 */
export const getMemoryInfo = (): {
  used: number | null;
  total: number | null;
  jsHeapSizeLimit: number | null;
} => {
  if ((navigator as any).deviceMemory) {
    // Device memory in GB
    return {
      used: null,
      total: (navigator as any).deviceMemory * 1024 * 1024 * 1024, // Convert to bytes
      jsHeapSizeLimit: null
    };
  }

  if ((window.performance as any).memory) {
    // Chrome-specific memory info
    const memory = (window.performance as any).memory;
    return {
      used: memory.usedJSHeapSize,
      total: memory.totalJSHeapSize,
      jsHeapSizeLimit: memory.jsHeapSizeLimit
    };
  }

  return {
    used: null,
    total: null,
    jsHeapSizeLimit: null
  };
};

/**
 * Debounce a function call
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>): void => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Throttle a function call
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>): void => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * Calculate estimated rendering time per frame
 */
export const calculateFrameBudget = (targetFPS: number = 60): number => {
  return 1000 / targetFPS; // ms per frame
};

/**
 * Check if current frame rate is within acceptable range
 */
export const isFrameRateAcceptable = (currentFPS: number, targetFPS: number = 60): boolean => {
  // Allow 10% tolerance
  return currentFPS >= targetFPS * 0.9;
};

/**
 * Measure frame render time using requestAnimationFrame
 */
export const measureFrameRenderTime = (callback: (renderTime: number) => void, framesToMeasure: number = 60): () => void => {
  let frameCount = 0;
  let totalRenderTime = 0;
  let lastFrameTime = 0;
  let animationFrameId: number;

  const measure = (timestamp: number) => {
    if (lastFrameTime > 0) {
      const frameRenderTime = timestamp - lastFrameTime;
      totalRenderTime += frameRenderTime;
      frameCount++;

      if (frameCount === framesToMeasure) {
        const avgRenderTime = totalRenderTime / frameCount;
        callback(avgRenderTime);
        // Reset for continuous monitoring
        frameCount = 0;
        totalRenderTime = 0;
      }
    }

    lastFrameTime = timestamp;
    animationFrameId = requestAnimationFrame(measure);
  };

  animationFrameId = requestAnimationFrame(measure);

  // Return a function to stop monitoring
  return () => {
    cancelAnimationFrame(animationFrameId);
  };
};

/**
 * Check if frame render time is within acceptable range (<16ms for 60fps)
 */
export const isFrameRenderTimeAcceptable = (renderTime: number, targetRenderTime: number = 16): boolean => {
  return renderTime <= targetRenderTime;
};

/**
 * Measure input delay by tracking time between user input and response
 */
export class InputDelayMeasurer {
  private startTime: number | null;
  private callback: (delay: number) => void;

  constructor(callback: (delay: number) => void) {
    this.startTime = null;
    this.callback = callback;
  }

  /**
   * Call this method when user input occurs
   */
  recordInput(): void {
    this.startTime = performance.now();
  }

  /**
   * Call this method when the response to user input is rendered
   */
  recordResponse(): void {
    if (this.startTime !== null) {
      const delay = performance.now() - this.startTime;
      this.callback(delay);
      this.startTime = null;
    }
  }

  /**
   * Measure input delay for a specific interaction
   */
  measureInteraction(interactionFn: () => void): void {
    this.recordInput();

    // Use setTimeout to ensure the interaction happens after the input recording
    setTimeout(() => {
      interactionFn();
      this.recordResponse();
    }, 0);
  }
}

/**
 * Check if input delay is within acceptable range (<50ms)
 */
export const isInputDelayAcceptable = (delay: number, targetDelay: number = 50): boolean => {
  return delay <= targetDelay;
};

/**
 * Performance observer for long tasks that may cause input delay
 */
export const observeLongTasks = (callback: (entry: PerformanceEntry) => void): PerformanceObserver | null => {
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach(entry => {
        if (entry.duration > 50) { // Tasks longer than 50ms
          callback(entry);
        }
      });
    });

    observer.observe({ entryTypes: ['longtask'] });
    return observer;
  }

  console.warn('PerformanceObserver not supported in this browser');
  return null;
};