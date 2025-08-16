/**
 * Media Service - 미디어/파일 관련 API 호출
 */

import { ApiClient, ApiError } from '../client';
import {
  UploadMediaResponse,
  GetMediaResponse,
  DeleteMediaResponse,
  Media
} from '@/types';

export class MediaService {
  constructor(private client: ApiClient) {}

  /**
   * 파일 업로드
   */
  async uploadMedia(
    file: File,
    targetType: 'project' | 'note',
    targetId: string,
    altText?: string
  ): Promise<UploadMediaResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('target_type', targetType);
      formData.append('target_id', targetId);
      
      if (altText) {
        formData.append('alt_text', altText);
      }

      return await this.client.upload<UploadMediaResponse>('/api/media/upload', formData);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'UPLOAD_MEDIA_FAILED',
        'Failed to upload media',
        500,
        { originalError: error, fileName: file.name, targetType, targetId }
      );
    }
  }

  /**
   * 미디어 정보 조회
   */
  async getMedia(id: string): Promise<GetMediaResponse> {
    try {
      return await this.client.get<GetMediaResponse>(`/api/media/${id}`);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_MEDIA_FAILED',
        'Failed to fetch media',
        500,
        { originalError: error, mediaId: id }
      );
    }
  }

  /**
   * 미디어 삭제
   */
  async deleteMedia(id: string): Promise<DeleteMediaResponse> {
    try {
      return await this.client.delete<DeleteMediaResponse>(`/api/media/${id}`);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'DELETE_MEDIA_FAILED',
        'Failed to delete media',
        500,
        { originalError: error, mediaId: id }
      );
    }
  }

  /**
   * 프로젝트 미디어 목록 조회
   */
  async getProjectMedia(projectId: string): Promise<Media[]> {
    try {
      const response = await this.client.get<{ media: Media[] }>(`/api/projects/${projectId}/media`);
      return response.media;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_PROJECT_MEDIA_FAILED',
        'Failed to fetch project media',
        500,
        { originalError: error, projectId }
      );
    }
  }

  /**
   * 노트 미디어 목록 조회
   */
  async getNoteMedia(noteId: string): Promise<Media[]> {
    try {
      const response = await this.client.get<{ media: Media[] }>(`/api/notes/${noteId}/media`);
      return response.media;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_NOTE_MEDIA_FAILED',
        'Failed to fetch note media',
        500,
        { originalError: error, noteId }
      );
    }
  }

  /**
   * 다중 파일 업로드
   */
  async uploadMultipleMedia(
    files: File[],
    targetType: 'project' | 'note',
    targetId: string
  ): Promise<UploadMediaResponse[]> {
    try {
      const uploadPromises = files.map(file => 
        this.uploadMedia(file, targetType, targetId)
      );
      
      return await Promise.all(uploadPromises);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'UPLOAD_MULTIPLE_MEDIA_FAILED',
        'Failed to upload multiple media files',
        500,
        { originalError: error, fileCount: files.length, targetType, targetId }
      );
    }
  }

  /**
   * 이미지 URL 생성 (다운로드/프리뷰용)
   */
  async getMediaUrl(id: string, type: 'download' | 'preview' = 'preview'): Promise<string> {
    try {
      const response = await this.client.get<{ url: string }>(`/api/media/${id}/url`, { type });
      return response.url;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'GET_MEDIA_URL_FAILED',
        'Failed to get media URL',
        500,
        { originalError: error, mediaId: id, type }
      );
    }
  }

  /**
   * 미디어 메타데이터 업데이트
   */
  async updateMediaMetadata(id: string, data: { alt_text?: string; is_public?: boolean }): Promise<Media> {
    try {
      const response = await this.client.patch<{ media: Media }>(`/api/media/${id}`, data);
      return response.media;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        'UPDATE_MEDIA_METADATA_FAILED',
        'Failed to update media metadata',
        500,
        { originalError: error, mediaId: id }
      );
    }
  }

  /**
   * 파일 형식 검증
   */
  validateFileType(file: File, allowedTypes: string[]): boolean {
    return allowedTypes.includes(file.type);
  }

  /**
   * 파일 크기 검증
   */
  validateFileSize(file: File, maxSizeInMB: number): boolean {
    const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
    return file.size <= maxSizeInBytes;
  }

  /**
   * 이미지 파일인지 확인
   */
  isImageFile(file: File): boolean {
    return file.type.startsWith('image/');
  }

  /**
   * 비디오 파일인지 확인
   */
  isVideoFile(file: File): boolean {
    return file.type.startsWith('video/');
  }

  /**
   * 문서 파일인지 확인
   */
  isDocumentFile(file: File): boolean {
    const documentTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'text/markdown'
    ];
    return documentTypes.includes(file.type);
  }
}