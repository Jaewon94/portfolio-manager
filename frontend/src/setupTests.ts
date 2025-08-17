/**
 * Jest 테스트 환경 설정
 */

// Jest DOM matchers 추가
import '@testing-library/jest-dom';

// Global test utilities
global.console.warn = jest.fn();
global.console.error = jest.fn();

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  root: Element | null = null;
  rootMargin: string = '0px';
  thresholds: ReadonlyArray<number> = [0];

  constructor(
    callback: IntersectionObserverCallback,
    options?: IntersectionObserverInit
  ) {
    // Mock implementation - parameters intentionally unused for testing
    void callback;
    void options;
  }

  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }
} as typeof IntersectionObserver;

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {
    return null;
  }
  disconnect() {
    return null;
  }
  unobserve() {
    return null;
  }
};

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
    protocol: 'http:',
    host: 'localhost:3000',
    hostname: 'localhost',
    port: '3000',
    pathname: '/',
    search: '',
    hash: '',
    ancestorOrigins: {} as DOMStringList,
    assign: jest.fn(),
    reload: jest.fn(),
    replace: jest.fn(),
  },
  writable: true,
});

// Mock URLSearchParams
global.URLSearchParams = class URLSearchParams {
  private params = new Map<string, string>();

  get size(): number {
    return this.params.size;
  }

  constructor(init?: string | string[][] | Record<string, string>) {
    if (typeof init === 'string') {
      // Simple parsing for test purposes
      const pairs = init.split('&');
      for (const pair of pairs) {
        const [key, value] = pair.split('=');
        if (key)
          this.params.set(
            decodeURIComponent(key),
            decodeURIComponent(value || '')
          );
      }
    } else if (Array.isArray(init)) {
      for (const [key, value] of init) {
        this.params.set(key, value);
      }
    } else if (init && typeof init === 'object') {
      for (const [key, value] of Object.entries(init)) {
        this.params.set(key, value);
      }
    }
  }

  append(name: string, value: string): void {
    this.params.set(name, value);
  }

  delete(name: string): void {
    this.params.delete(name);
  }

  get(name: string): string | null {
    return this.params.get(name) || null;
  }

  getAll(name: string): string[] {
    const value = this.params.get(name);
    return value ? [value] : [];
  }

  has(name: string): boolean {
    return this.params.has(name);
  }

  set(name: string, value: string): void {
    this.params.set(name, value);
  }

  sort(): void {
    // Simple mock implementation
  }

  forEach(
    callback: (value: string, key: string, parent: URLSearchParams) => void
  ): void {
    for (const [key, value] of this.params) {
      callback(value, key, this);
    }
  }

  entries(): IterableIterator<[string, string]> {
    return this.params.entries();
  }

  keys(): IterableIterator<string> {
    return this.params.keys();
  }

  values(): IterableIterator<string> {
    return this.params.values();
  }

  toString(): string {
    const pairs: string[] = [];
    for (const [key, value] of this.params) {
      pairs.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
    }
    return pairs.join('&');
  }

  *[Symbol.iterator](): IterableIterator<[string, string]> {
    yield* this.params;
  }
} as unknown as typeof URLSearchParams;

// File API mocks for media tests
global.File = class File {
  name: string;
  size: number;
  type: string;
  lastModified: number;

  constructor(
    chunks: (string | ArrayBuffer)[],
    filename: string,
    options: { type?: string } = {}
  ) {
    this.name = filename;
    this.type = options.type || '';
    this.size = chunks.reduce((size, chunk) => {
      if (typeof chunk === 'string') return size + chunk.length;
      return size + chunk.byteLength;
    }, 0);
    this.lastModified = Date.now();
  }
} as typeof File;

global.FormData = class FormData {
  private data = new Map<string, FormDataEntryValue>();

  append(name: string, value: FormDataEntryValue): void {
    this.data.set(name, value);
  }

  get(name: string): FormDataEntryValue | null {
    return this.data.get(name) || null;
  }

  getAll(name: string): FormDataEntryValue[] {
    const value = this.data.get(name);
    return value ? [value] : [];
  }

  has(name: string): boolean {
    return this.data.has(name);
  }

  set(name: string, value: FormDataEntryValue): void {
    this.data.set(name, value);
  }

  delete(name: string): void {
    this.data.delete(name);
  }

  forEach(
    callback: (value: FormDataEntryValue, key: string, parent: FormData) => void
  ): void {
    for (const [key, value] of this.data) {
      callback(value, key, this);
    }
  }

  entries(): IterableIterator<[string, FormDataEntryValue]> {
    return this.data.entries();
  }

  keys(): IterableIterator<string> {
    return this.data.keys();
  }

  values(): IterableIterator<FormDataEntryValue> {
    return this.data.values();
  }

  *[Symbol.iterator](): IterableIterator<[string, FormDataEntryValue]> {
    yield* this.data;
  }
} as unknown as typeof FormData;
