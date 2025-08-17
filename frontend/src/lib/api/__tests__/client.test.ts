/**
 * API Client 테스트
 */

import { ApiClient, ApiError } from '../client';

// Mock fetch
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('ApiClient', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient({
      baseUrl: 'http://localhost:8000',
      timeout: 5000,
    });
    mockFetch.mockClear();
  });

  describe('constructor', () => {
    it('should initialize with default config', () => {
      const defaultClient = new ApiClient({ baseUrl: 'http://localhost:8000' });
      expect(defaultClient).toBeInstanceOf(ApiClient);
    });

    it('should initialize with custom config', () => {
      const customClient = new ApiClient({
        baseUrl: 'https://api.example.com',
        timeout: 10000,
        defaultHeaders: { 'Custom-Header': 'value' },
      });
      expect(customClient).toBeInstanceOf(ApiClient);
    });
  });

  describe('GET requests', () => {
    it('should make GET request successfully', async () => {
      const mockData = { id: 1, name: 'Test' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await client.get('/test');
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'GET',
          headers: expect.any(Object),
        })
      );
      expect(result).toEqual(mockData);
    });

    it('should handle GET request with query parameters', async () => {
      const mockData = { results: [] };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const params = { page: 1, limit: 10, search: 'test query' };
      await client.get('/search', params);
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/search?page=1&limit=10&search=test%20query',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });
  });

  describe('POST requests', () => {
    it('should make POST request successfully', async () => {
      const requestData = { name: 'New Item', description: 'Test description' };
      const responseData = { id: 1, ...requestData };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => responseData,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await client.post('/items', requestData);
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/items',
        expect.objectContaining({
          method: 'POST',
          headers: expect.any(Object),
          body: JSON.stringify(requestData),
        })
      );
      expect(result).toEqual(responseData);
    });
  });

  describe('PATCH requests', () => {
    it('should make PATCH request successfully', async () => {
      const updateData = { name: 'Updated Name' };
      const responseData = { id: 1, name: 'Updated Name', description: 'Test' };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => responseData,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await client.patch('/items/1', updateData);
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/items/1',
        expect.objectContaining({
          method: 'PATCH',
          headers: expect.any(Object),
          body: JSON.stringify(updateData),
        })
      );
      expect(result).toEqual(responseData);
    });
  });

  describe('DELETE requests', () => {
    it('should make DELETE request successfully', async () => {
      const responseData = { deleted: true, id: '1' };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => responseData,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await client.delete('/items/1');
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/items/1',
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.any(Object),
        })
      );
      expect(result).toEqual(responseData);
    });
  });

  describe('File upload', () => {
    it('should handle file upload successfully', async () => {
      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      const formData = new FormData();
      formData.append('file', file);
      
      const responseData = { id: 1, filename: 'test.txt' };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => responseData,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await client.upload('/upload', formData);
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/upload',
        expect.objectContaining({
          method: 'POST',
          body: formData,
        })
      );
      expect(result).toEqual(responseData);
    });
  });

  describe('Error handling', () => {
    it('should throw ApiError for HTTP error responses', async () => {
      const errorResponse = {
        error: {
          code: 'NOT_FOUND',
          message: 'Resource not found',
        },
      };
      
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => errorResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const promise = client.get('/not-found');
      await expect(promise).rejects.toThrow(ApiError);
      
      // Set up the same mock for the second test
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => errorResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);
      
      await expect(client.get('/not-found')).rejects.toThrow('Resource not found');
    });

    it('should throw ApiError for network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(client.get('/test')).rejects.toThrow(ApiError);
      await expect(client.get('/test')).rejects.toThrow('Network error occurred');
    });

    it('should throw ApiError for timeout', async () => {
      const shortTimeoutClient = new ApiClient({
        baseUrl: 'http://localhost:8000',
        timeout: 100,
      });

      mockFetch.mockImplementationOnce(
        () => new Promise(resolve => setTimeout(resolve, 200))
      );

      await expect(shortTimeoutClient.get('/slow')).rejects.toThrow(ApiError);
      await expect(shortTimeoutClient.get('/slow')).rejects.toThrow('Network error occurred');
    });
  });

  describe('Authentication', () => {
    it('should set bearer token in headers', async () => {
      client.setAuthToken('test-token');
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      await client.get('/protected');
      
      const call = mockFetch.mock.calls[0];
      const headers = call[1]?.headers as Record<string, string>;
      expect(headers['Authorization']).toBe('Bearer test-token');
    });

    it('should clear auth token', async () => {
      client.setAuthToken('test-token');
      client.removeAuthToken(); // Use removeAuthToken method
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      await client.get('/test');
      
      const call = mockFetch.mock.calls[0];
      const headers = call[1]?.headers as Record<string, string>;
      expect(headers['Authorization']).toBeUndefined();
    });
  });

  describe('Content type handling', () => {
    it('should handle JSON responses', async () => {
      const mockData = { message: 'success' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await client.get('/json');
      expect(result).toEqual(mockData);
    });

    it('should handle text responses', async () => {
      const mockText = 'Plain text response';
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        text: async () => mockText,
        json: async () => { throw new Error('Not JSON'); },
        headers: new Headers({ 'content-type': 'text/plain' }),
      } as Response);

      const result = await client.get('/text');
      expect(result).toBe(mockText);
    });
  });
});

describe('ApiError', () => {
  it('should create ApiError with all properties', () => {
    const error = new ApiError(
      'TEST_ERROR',
      'Test error message',
      400,
      { detail: 'Additional details' }
    );

    expect(error).toBeInstanceOf(Error);
    expect(error.name).toBe('ApiError');
    expect(error.code).toBe('TEST_ERROR');
    expect(error.message).toBe('Test error message');
    expect(error.status).toBe(400);
    expect(error.details).toEqual({ detail: 'Additional details' });
  });

  it('should have default status', () => {
    const error = new ApiError('ERROR', 'Message', 400);
    expect(error.status).toBe(400);
  });

  it('should serialize to JSON correctly', () => {
    const error = new ApiError(
      'SERIALIZE_TEST',
      'Serialization test',
      422,
      { field: 'invalid' }
    );

    const serialized = JSON.stringify(error);
    const parsed = JSON.parse(serialized);

    expect(parsed.name).toBe('ApiError');
    expect(parsed.code).toBe('SERIALIZE_TEST');
    expect(parsed.message).toBe('Serialization test');
    expect(parsed.status).toBe(422);
    expect(parsed.details).toEqual({ field: 'invalid' });
  });
});