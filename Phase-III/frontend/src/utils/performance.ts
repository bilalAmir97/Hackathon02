/**
 * Performance utilities for the soft dark theme dashboard
 */

/**
 * Measures the frame rate of an animation
 */
export const measureFrameRate = (callback: () => void, iterations: number = 100): Promise<number> => {
  return new Promise((resolve) => {
    let frameCount = 0;
    let startTime: number;

    const measure = (timestamp: number) => {
      if (frameCount === 0) {
        startTime = timestamp;
      }

      callback();
      frameCount++;

      if (frameCount < iterations) {
        requestAnimationFrame(measure);
      } else {
        const endTime = timestamp;
        const elapsed = (endTime - startTime) / 1000; // in seconds
        const fps = frameCount / elapsed;
        resolve(fps);
      }
    };

    requestAnimationFrame(measure);
  });
};

/**
 * Debounces a function call
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttles a function call
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * Memoizes a function
 */
export const memoize = <T extends (...args: any[]) => any>(func: T): T => {
  const cache = new Map<string, ReturnType<T>>();

  return ((...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key)!;
    }

    const result = func(...args);
    cache.set(key, result);
    return result;
  }) as T;
};

/**
 * Measures memory usage (where available)
 */
export const measureMemoryUsage = (): { used: number; total: number; limit: number } | null => {
  if ('memory' in performance) {
    // @ts-ignore - memory property is not standard
    const memoryInfo = performance.memory;
    return {
      used: memoryInfo.usedJSHeapSize,
      total: memoryInfo.totalJSHeapSize,
      limit: memoryInfo.jsHeapSizeLimit
    };
  }
  return null;
};

/**
 * Tracks performance of a function
 */
export const trackPerformance = async <T>(
  fn: () => T | Promise<T>,
  label: string
): Promise<{ result: T; duration: number; memoryBefore?: any; memoryAfter?: any }> => {
  const memoryBefore = measureMemoryUsage();
  const start = performance.now();

  try {
    const result = await Promise.resolve(fn());
    const end = performance.now();
    const memoryAfter = measureMemoryUsage();

    console.group(`Performance: ${label}`);
    console.log(`Duration: ${end - start} ms`);
    if (memoryBefore && memoryAfter) {
      console.log(`Memory change: ${((memoryAfter.used - memoryBefore.used) / 1024 / 1024).toFixed(2)} MB`);
    }
    console.groupEnd();

    return { result, duration: end - start, memoryBefore, memoryAfter };
  } catch (error) {
    const end = performance.now();
    console.error(`Performance tracking error for ${label}:`, error);
    return Promise.reject({ error, duration: end - start });
  }
};

/**
 * Implements virtual scrolling for large lists
 */
export class VirtualScroller {
  private container: HTMLElement;
  private items: HTMLElement[];
  private itemHeight: number;
  private visibleItems: number;
  private scrollTop: number = 0;

  constructor(container: HTMLElement, items: HTMLElement[], itemHeight: number) {
    this.container = container;
    this.items = items;
    this.itemHeight = itemHeight;
    this.visibleItems = Math.ceil(container.clientHeight / itemHeight) + 2; // Add buffer

    this.init();
  }

  private init() {
    this.container.addEventListener('scroll', this.handleScroll.bind(this));
    this.render();
  }

  private handleScroll() {
    this.scrollTop = this.container.scrollTop;
    this.render();
  }

  private render() {
    const startIndex = Math.floor(this.scrollTop / this.itemHeight);
    const endIndex = Math.min(startIndex + this.visibleItems, this.items.length);

    // Hide all items first
    this.items.forEach(item => {
      item.style.display = 'none';
    });

    // Show only visible items
    for (let i = startIndex; i < endIndex; i++) {
      if (this.items[i]) {
        this.items[i].style.display = 'block';
        this.items[i].style.transform = `translateY(${i * this.itemHeight}px)`;
      }
    }
  }

  public updateItems(newItems: HTMLElement[]) {
    this.items = newItems;
    this.render();
  }

  public destroy() {
    this.container.removeEventListener('scroll', this.handleScroll.bind(this));
  }
}

/**
 * Implements lazy loading for images
 */
export const lazyLoadImage = (img: HTMLImageElement, src: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const imageLoader = new Image();
    imageLoader.onload = () => {
      img.src = src;
      resolve();
    };
    imageLoader.onerror = reject;
    imageLoader.src = src;
  });
};