export interface CommentMention {
  userId: string;
  displayName?: string;
  email?: string;
  avatarUrl?: string | null;
}

export interface Comment {
  id: string;
  entityType: string;
  entityId: string;
  parentCommentId: string | null;
  authorId: string;
  authorName: string;
  avatarUrl: string | null;
  content: string;
  mentions: CommentMention[];
  isEdited: boolean;
  createdAt: string;
  updatedAt: string;
  replies: Comment[];
}

export interface CommentListParams {
  entityType: string;
  entityId: string;
}

export interface CommentCreatePayload {
  entityType: string;
  entityId: string;
  content: string;
  mentions?: CommentMention[];
  parentCommentId?: string | null;
}

export interface CommentUpdatePayload {
  commentId: string;
  content: string;
  mentions?: CommentMention[];
}

export interface CommentDeletePayload {
  commentId: string;
  force?: boolean;
}

export interface MentionSuggestion {
  userId: string;
  displayName: string;
  email?: string;
  avatarUrl?: string | null;
}
