import { act, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import CommentThread from '../CommentThread';
import type { Comment, CommentMention } from '../../../types/comments';

const mockListComments = vi.fn();
const mockCreateComment = vi.fn();
const mockUpdateComment = vi.fn();
const mockDeleteComment = vi.fn();
const mockSuggestMentions = vi.fn();

vi.mock('../../../services/comment.service', () => ({
  listComments: (params: unknown) => mockListComments(params as Record<string, unknown> | undefined),
  createComment: (payload: unknown) => mockCreateComment(payload),
  updateComment: (payload: unknown) => mockUpdateComment(payload),
  deleteComment: (payload: unknown) => mockDeleteComment(payload),
  suggestMentions: (query: unknown) => mockSuggestMentions(query),
}));

const baseComment: Comment = {
  id: 'comment-1',
  entityType: 'test_case',
  entityId: 'case-123',
  parentCommentId: null,
  authorId: 'user-1',
  authorName: 'Alice Example',
  avatarUrl: null,
  content: 'Initial comment',
  mentions: [],
  isEdited: false,
  createdAt: '2025-03-21T10:00:00Z',
  updatedAt: '2025-03-21T10:00:00Z',
  replies: [],
};

const currentUser = {
  id: 'user-1',
  name: 'Alice Example',
  avatarUrl: null,
};

describe('CommentThread', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it.only('renders comments and replies returned by the service', async () => {
    const reply: Comment = {
      ...baseComment,
      id: 'comment-2',
      parentCommentId: 'comment-1',
      authorId: 'user-2',
      authorName: 'Bob Reviewer',
      content: 'Reply message',
    };

    const root: Comment = {
      ...baseComment,
      replies: [reply],
    };

    mockListComments.mockResolvedValueOnce([root]);

    render(
      <CommentThread entityType="test_case" entityId="case-123" currentUser={currentUser} />
    );
    console.log('component rendered');

    expect(mockListComments).toHaveBeenNthCalledWith(1, {
      entityType: 'test_case',
      entityId: 'case-123',
    });

    expect(await screen.findByText(/Initial comment/i)).toBeInTheDocument();
    expect(screen.getByText(/Reply message/i)).toBeInTheDocument();

    const replySection = screen.getByTestId('comment-replies-comment-1');
    expect(within(replySection).getByText(/Reply message/i)).toBeInTheDocument();
  });

  it('allows the current user to create a new comment with mentions', async () => {
    mockListComments.mockResolvedValueOnce([]);

    const mentionSuggestions: CommentMention[] = [
      {
        userId: 'user-2',
        displayName: 'Bob Reviewer',
        email: 'bob@example.com',
      },
    ];

    mockSuggestMentions.mockResolvedValue(mentionSuggestions);

    const createdComment: Comment = {
      ...baseComment,
      id: 'comment-3',
      content: 'Hello @Bob Reviewer this is a new comment',
      mentions: mentionSuggestions,
    };

    mockCreateComment.mockResolvedValueOnce(createdComment);
    mockListComments.mockResolvedValueOnce([createdComment]);

    render(
      <CommentThread entityType="test_case" entityId="case-123" currentUser={currentUser} />
    );

    const composer = await screen.findByLabelText(/Add a comment/i);

    const user = userEvent.setup();

    await user.type(composer, 'Hello @Bo');

    await waitFor(() => {
      expect(mockSuggestMentions).toHaveBeenCalledWith('Bo');
    });

    const suggestion = await screen.findByRole('option', { name: /Bob Reviewer/i });
    await user.click(suggestion);

    expect(composer).toHaveValue('Hello @Bob Reviewer ');

    await user.type(composer, 'this is a new comment');
    await user.click(screen.getByRole('button', { name: /Post comment/i }));

    await waitFor(() => {
      expect(mockCreateComment).toHaveBeenCalledWith({
        entityType: 'test_case',
        entityId: 'case-123',
        content: 'Hello @Bob Reviewer this is a new comment',
        mentions: mentionSuggestions,
        parentCommentId: null,
      });
    });

    expect(await screen.findByText(/Hello @Bob Reviewer this is a new comment/i)).toBeInTheDocument();
    expect(mockListComments).toHaveBeenNthCalledWith(1, {
      entityType: 'test_case',
      entityId: 'case-123',
    });
    expect(mockListComments).toHaveBeenNthCalledWith(2, {
      entityType: 'test_case',
      entityId: 'case-123',
    });
  });

  it('allows editing a comment authored by the current user', async () => {
    mockListComments.mockResolvedValueOnce([baseComment]);

    const updated = {
      ...baseComment,
      content: 'Updated comment content',
      isEdited: true,
    };

    mockUpdateComment.mockResolvedValueOnce(updated);
    mockListComments.mockResolvedValueOnce([updated]);

    render(
      <CommentThread entityType="test_case" entityId="case-123" currentUser={currentUser} />
    );

    await screen.findByText(/Initial comment/i);

    const user = userEvent.setup();

    await user.click(screen.getByRole('button', { name: /Edit comment/i }));

    const editor = screen.getByLabelText(/Edit your comment/i);

    await act(async () => {
      await user.clear(editor);
      await user.type(editor, 'Updated comment content');
    });

    await user.click(screen.getByRole('button', { name: /Save changes/i }));

    await waitFor(() => {
      expect(mockUpdateComment).toHaveBeenCalledWith({
        commentId: 'comment-1',
        content: 'Updated comment content',
        mentions: [],
      });
    });

    expect(await screen.findByText(/Updated comment content/i)).toBeInTheDocument();
    expect(mockListComments).toHaveBeenNthCalledWith(1, {
      entityType: 'test_case',
      entityId: 'case-123',
    });
    expect(mockListComments).toHaveBeenNthCalledWith(2, {
      entityType: 'test_case',
      entityId: 'case-123',
    });
  });

  it('allows deleting a comment after confirmation', async () => {
    mockListComments.mockResolvedValueOnce([baseComment]);
    mockDeleteComment.mockResolvedValueOnce(true);
    mockListComments.mockResolvedValueOnce([]);

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

    render(
      <CommentThread entityType="test_case" entityId="case-123" currentUser={currentUser} />
    );

    await screen.findByText(/Initial comment/i);

    const user = userEvent.setup();

    await user.click(screen.getByRole('button', { name: /Delete comment/i }));

    await waitFor(() => {
      expect(mockDeleteComment).toHaveBeenCalledWith({
        commentId: 'comment-1',
      });
    });

    await waitFor(() => {
      expect(screen.queryByText(/Initial comment/i)).not.toBeInTheDocument();
    });

    expect(mockListComments).toHaveBeenNthCalledWith(1, {
      entityType: 'test_case',
      entityId: 'case-123',
    });
    expect(mockListComments).toHaveBeenNthCalledWith(2, {
      entityType: 'test_case',
      entityId: 'case-123',
    });
    confirmSpy.mockRestore();
  });
});
