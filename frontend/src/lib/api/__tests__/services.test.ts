/**
 * API Services 테스트
 */

import { ApiClient } from '../client';
import { ProjectsService } from '../services/projects';
import { NotesService } from '../services/notes';
import { SearchService } from '../services/search';
import { MediaService } from '../services/media';
import { AuthService } from '../services/auth';
import { ProjectVisibility, ProjectStatus, NoteType } from '@/types';

// Mock fetch for ApiClient
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('API Services', () => {
  let client: ApiClient;
  let authService: AuthService;
  let projectsService: ProjectsService;
  let notesService: NotesService;
  let searchService: SearchService;
  let mediaService: MediaService;

  beforeEach(() => {
    client = new ApiClient({
      baseUrl: 'http://localhost:8000',
      timeout: 5000,
    });
    
    authService = new AuthService(client);
    projectsService = new ProjectsService(client);
    notesService = new NotesService(client);
    searchService = new SearchService(client);
    mediaService = new MediaService(client);
    
    mockFetch.mockClear();
  });

  describe('AuthService', () => {
    it('should login with provider', async () => {
      const loginData = {
        provider: 'github',
        redirect_url: 'http://localhost:3000/callback',
      };
      
      const loginResponse = {
        user: { id: '1', email: 'test@example.com', name: 'Test User' },
        session_token: 'token123',
        expires: '2024-12-31T23:59:59Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => loginResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await authService.login(loginData);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/login',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(loginData),
        })
      );
      expect(result).toEqual(loginResponse);
    });

    it('should get current user', async () => {
      const userResponse = {
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
          projects: [],
        },
        session: {
          expires: '2024-12-31T23:59:59Z',
          ip_address: '127.0.0.1',
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => userResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await authService.me();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/me',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(userResponse);
    });

    it('should logout', async () => {
      const logoutData = { session_token: 'session123' };
      const logoutResponse = { success: true };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => logoutResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await authService.logout(logoutData);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/logout',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(logoutData),
        })
      );
      expect(result).toEqual(logoutResponse);
    });
  });

  describe('ProjectsService', () => {
    it('should get projects list', async () => {
      const projectsResponse = {
        projects: [
          {
            id: '1',
            title: 'Test Project',
            description: 'Description',
            visibility: ProjectVisibility.PUBLIC,
            status: ProjectStatus.PUBLISHED,
          },
        ],
        pagination: {
          total: 1,
          page: 1,
          pageSize: 10,
          totalPages: 1,
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => projectsResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await projectsService.getProjects({
        page: 1,
        limit: 10,
        visibility: ProjectVisibility.PUBLIC,
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/projects?page=1&limit=10&visibility=public',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(projectsResponse);
    });

    it('should create project', async () => {
      const createData = {
        title: 'New Project',
        description: 'New project description',
        content: { type: 'doc' },
        tech_stack: ['React', 'TypeScript'],
        categories: ['Web'],
        tags: ['frontend'],
        visibility: ProjectVisibility.PUBLIC,
        status: ProjectStatus.DRAFT,
      };

      const createResponse = {
        project: {
          id: '1',
          ...createData,
          owner_id: 'user1',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => createResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await projectsService.createProject(createData);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/projects',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(createData),
        })
      );
      expect(result).toEqual(createResponse);
    });

    it('should update project status', async () => {
      const updateResponse = {
        project: {
          id: '1',
          status: ProjectStatus.PUBLISHED,
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => updateResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await projectsService.updateProjectStatus('1', ProjectStatus.PUBLISHED);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/projects/1',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({ status: ProjectStatus.PUBLISHED }),
        })
      );
      expect(result).toEqual(updateResponse);
    });
  });

  describe('NotesService', () => {
    it('should get notes for project', async () => {
      const notesResponse = {
        notes: [
          {
            id: '1',
            title: 'Test Note',
            content: { type: 'doc' },
            type: NoteType.LEARN,
            project_id: 'proj1',
          },
        ],
        pagination: {
          total: 1,
          page: 1,
          pageSize: 10,
          totalPages: 1,
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => notesResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await notesService.getNotes('proj1', {
        type: NoteType.LEARN,
        page: 1,
        limit: 10,
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/projects/proj1/notes?project_id=proj1&type=learn&page=1&limit=10',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(notesResponse);
    });

    it('should create note', async () => {
      const createData = {
        title: 'New Note',
        content: { type: 'doc' },
        type: NoteType.CHANGE,
        tags: ['important'],
      };

      const createResponse = {
        note: {
          id: '1',
          ...createData,
          project_id: 'proj1',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => createResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await notesService.createNote('proj1', createData);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/projects/proj1/notes',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            project_id: 'proj1',
            ...createData,
          }),
        })
      );
      expect(result).toEqual(createResponse);
    });

    it('should toggle note pinned status', async () => {
      const updateResponse = {
        note: {
          id: '1',
          is_pinned: true,
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => updateResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await notesService.toggleNotePinned('1', true);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/notes/1',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({ is_pinned: true }),
        })
      );
      expect(result).toEqual(updateResponse);
    });

    it('should add tag to note', async () => {
      const noteResponse = {
        note: {
          id: '1',
          tags: ['existing-tag'],
        },
      };

      const updateResponse = {
        note: {
          id: '1',
          tags: ['existing-tag', 'new-tag'],
        },
      };

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => noteResponse,
          headers: new Headers({ 'content-type': 'application/json' }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => updateResponse,
          headers: new Headers({ 'content-type': 'application/json' }),
        } as Response);

      const result = await notesService.addNoteTag('1', 'new-tag');

      expect(mockFetch).toHaveBeenNthCalledWith(1,
        'http://localhost:8000/api/notes/1',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(mockFetch).toHaveBeenNthCalledWith(2,
        'http://localhost:8000/api/notes/1',
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({ tags: ['existing-tag', 'new-tag'] }),
        })
      );
      expect(result).toEqual(updateResponse);
    });
  });

  describe('SearchService', () => {
    it('should perform global search', async () => {
      const searchResponse = {
        results: {
          projects: [{ id: '1', title: 'Test Project' }],
          notes: [{ id: '1', title: 'Test Note' }],
          users: [{ id: '1', name: 'Test User' }],
        },
        total: 3,
        query: 'test',
        took_ms: 50,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => searchResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await searchService.search({
        query: 'test',
        type: 'all',
        limit: 10,
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/search?query=test&type=all&limit=10',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(searchResponse);
    });

    it('should get autocomplete suggestions', async () => {
      const autocompleteResponse = {
        suggestions: [
          { type: 'project', text: 'Test Project' },
          { type: 'tag', text: 'test-tag' },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => autocompleteResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await searchService.autocomplete({
        query: 'test',
        type: 'projects',
        limit: 5,
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/search/autocomplete?query=test&type=projects&limit=5',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(autocompleteResponse);
    });

    it('should search projects with filters', async () => {
      const searchResponse = {
        results: {
          projects: [{ id: '1', title: 'React Project' }],
        },
        total: 1,
        query: 'react',
        took_ms: 30,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => searchResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await searchService.searchProjects('react', {
        tech_stack: ['React'],
        categories: ['Web'],
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/search?query=react&type=projects&tech_stack=React&categories=Web',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual([{ id: '1', title: 'React Project' }]);
    });
  });

  describe('MediaService', () => {
    it('should upload media file', async () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
      const uploadResponse = {
        media: {
          id: '1',
          original_name: 'test.jpg',
          file_path: '/uploads/test.jpg',
          mime_type: 'image/jpeg',
          file_size: 1024,
        },
        upload_url: 'https://example.com/uploads/test.jpg',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => uploadResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      } as Response);

      const result = await mediaService.uploadMedia(file, 'project', 'proj1', 'Alt text');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/media/upload',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        })
      );
      expect(result).toEqual(uploadResponse);
    });

    it('should validate file type', () => {
      const imageFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
      const textFile = new File(['content'], 'test.txt', { type: 'text/plain' });

      expect(mediaService.validateFileType(imageFile, ['image/jpeg', 'image/png'])).toBe(true);
      expect(mediaService.validateFileType(textFile, ['image/jpeg', 'image/png'])).toBe(false);
    });

    it('should validate file size', () => {
      const smallFile = new File(['small'], 'small.txt', { type: 'text/plain' });
      const largeFile = new File([new ArrayBuffer(2 * 1024 * 1024)], 'large.bin');

      expect(mediaService.validateFileSize(smallFile, 1)).toBe(true);
      expect(mediaService.validateFileSize(largeFile, 1)).toBe(false);
    });

    it('should check if file is image', () => {
      const imageFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
      const textFile = new File(['content'], 'test.txt', { type: 'text/plain' });

      expect(mediaService.isImageFile(imageFile)).toBe(true);
      expect(mediaService.isImageFile(textFile)).toBe(false);
    });

    it('should upload multiple files', async () => {
      const files = [
        new File(['content1'], 'test1.jpg', { type: 'image/jpeg' }),
        new File(['content2'], 'test2.jpg', { type: 'image/jpeg' }),
      ];

      const uploadResponses = [
        { media: { id: '1', original_name: 'test1.jpg' } },
        { media: { id: '2', original_name: 'test2.jpg' } },
      ];

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          status: 201,
          json: async () => uploadResponses[0],
          headers: new Headers({ 'content-type': 'application/json' }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          status: 201,
          json: async () => uploadResponses[1],
          headers: new Headers({ 'content-type': 'application/json' }),
        } as Response);

      const result = await mediaService.uploadMultipleMedia(files, 'project', 'proj1');

      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(result).toEqual(uploadResponses);
    });
  });
});