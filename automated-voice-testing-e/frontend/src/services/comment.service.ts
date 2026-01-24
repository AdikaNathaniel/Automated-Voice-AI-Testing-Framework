import apiClient from './api';
import type {
  Comment,
  CommentCreatePayload,
  CommentDeletePayload,
  CommentListParams,
  CommentMention,
  CommentUpdatePayload,
  MentionSuggestion,
} from '../types/comments';

type ApiCommentMention = {
  user_id?: string;
  display_name?: string;
  email?: string;
  avatar_url?: string | null;
};

type ApiComment = {
  id?: string;
  entity_type?: string;
  entity_id?: string;
  parent_comment_id?: string | null;
  author_id?: string;
  author_name?: string;
  author_avatar_url?: string | null;
  content?: string;
  mentions?: ApiCommentMention[];
  is_edited?: boolean;
  created_at?: string;
  updated_at?: string;
  replies?: ApiComment[];
};

type ApiMentionSuggestion = {
  user_id?: string;
  display_name?: string;
  email?: string;
  avatar_url?: string | null;
};

const mapMention = (mention: ApiCommentMention | ApiMentionSuggestion | undefined): CommentMention => ({
  userId: mention?.user_id ?? '',
  displayName: mention?.display_name ?? undefined,
  email: mention?.email ?? undefined,
  avatarUrl: mention?.avatar_url ?? null,
});

const mapComment = (comment: ApiComment): Comment => {
  const mentions = Array.isArray(comment.mentions) ? comment.mentions : [];
  const replies = Array.isArray(comment.replies) ? comment.replies : [];

  return {
    id: comment.id ?? 'unknown',
    entityType: comment.entity_type ?? 'unknown',
    entityId: comment.entity_id ?? 'unknown',
    parentCommentId: comment.parent_comment_id ?? null,
    authorId: comment.author_id ?? 'unknown',
    authorName: comment.author_name ?? 'Unknown user',
    avatarUrl: comment.author_avatar_url ?? null,
    content: comment.content ?? '',
    mentions: mentions.map(mapMention),
    isEdited: Boolean(comment.is_edited),
    createdAt: comment.created_at ?? '',
    updatedAt: comment.updated_at ?? comment.created_at ?? '',
    replies: replies.map(mapComment),
  };
};

const serialiseMentions = (mentions?: CommentMention[]) =>
  (mentions ?? []).map((mention) => ({
    user_id: mention.userId,
    display_name: mention.displayName,
    email: mention.email,
    avatar_url: mention.avatarUrl ?? null,
  }));

export class CommentServiceError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = 'CommentServiceError';
  }
}

export const listComments = async (params: CommentListParams): Promise<Comment[]> => {
  try {
    const response = await apiClient.get<ApiComment[]>('/comments', {
      params: {
        entity_type: params.entityType,
        entity_id: params.entityId,
        include_replies: true,
      },
    });

    const payload = Array.isArray(response.data) ? response.data : [];
    return payload.map(mapComment);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to fetch comments';
    throw new CommentServiceError(message, error);
  }
};

export const createComment = async (payload: CommentCreatePayload): Promise<Comment> => {
  try {
    const response = await apiClient.post<ApiComment>('/comments', {
      entity_type: payload.entityType,
      entity_id: payload.entityId,
      content: payload.content,
      parent_comment_id: payload.parentCommentId ?? null,
      mentions: serialiseMentions(payload.mentions),
    });

    return mapComment(response.data ?? {});
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to create comment';
    throw new CommentServiceError(message, error);
  }
};

export const updateComment = async (payload: CommentUpdatePayload): Promise<Comment> => {
  try {
    const response = await apiClient.patch<ApiComment>(`/comments/${payload.commentId}`, {
      content: payload.content,
      mentions: serialiseMentions(payload.mentions),
    });

    return mapComment(response.data ?? {});
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to update comment';
    throw new CommentServiceError(message, error);
  }
};

export const deleteComment = async (payload: CommentDeletePayload): Promise<boolean> => {
  try {
    const response = await apiClient.delete<{ deleted?: boolean }>(`/comments/${payload.commentId}`, {
      params: {
        force: payload.force ?? false,
      },
    });

    return Boolean(response.data?.deleted ?? true);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to delete comment';
    throw new CommentServiceError(message, error);
  }
};

export const suggestMentions = async (query: string): Promise<MentionSuggestion[]> => {
  try {
    const response = await apiClient.get<ApiMentionSuggestion[]>('/comments/mentions', {
      params: {
        q: query,
      },
    });

    const suggestions = Array.isArray(response.data) ? response.data : [];
    return suggestions.map(mapMention);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Failed to fetch mention suggestions';
    throw new CommentServiceError(message, error);
  }
};

export default {
  listComments,
  createComment,
  updateComment,
  deleteComment,
  suggestMentions,
};
