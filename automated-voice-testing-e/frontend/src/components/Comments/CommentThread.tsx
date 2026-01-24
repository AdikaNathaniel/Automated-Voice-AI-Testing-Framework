import { useCallback, useEffect, useState } from 'react';

import {
  createComment,
  deleteComment,
  listComments,
  suggestMentions,
  updateComment,
} from '../../services/comment.service';
import type {
  Comment,
  CommentMention,
  MentionSuggestion,
} from '../../types/comments';
import Modal from '../Modal/Modal';
import { useModal } from '../../hooks/useModal';

type CommentThreadProps = {
  entityType: string;
  entityId: string;
  currentUser: {
    id: string;
    name: string;
    avatarUrl?: string | null;
  };
};

type MentionContext = {
  start: number;
  end: number;
  query: string;
};

type ComposerSubmitPayload = {
  content: string;
  mentions: CommentMention[];
};

type CommentComposerProps = {
  id: string;
  label: string;
  placeholder?: string;
  submitLabel: string;
  initialValue?: string;
  initialMentions?: CommentMention[];
  autoFocus?: boolean;
  onSubmit: (payload: ComposerSubmitPayload) => Promise<void> | void;
  onCancel?: () => void;
};

const MIN_MENTION_QUERY = 2;

const formatTimestamp = (value: string) => {
  if (!value) {
    return '';
  }

  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString();
  } catch {
    return value;
  }
};

const normaliseComments = (items: Comment[]): Comment[] =>
  items.map((item) => ({
    ...item,
    replies: Array.isArray(item.replies) ? normaliseComments(item.replies) : [],
  }));

const CommentComposer = ({
  id,
  label,
  placeholder,
  submitLabel,
  initialValue = '',
  initialMentions = [],
  autoFocus = false,
  onSubmit,
  onCancel,
}: CommentComposerProps) => {
  const [value, setValue] = useState(initialValue);
  const [mentions, setMentions] = useState<CommentMention[]>(initialMentions);
  const [mentionContext, setMentionContext] = useState<MentionContext | null>(null);
  const [suggestions, setSuggestions] = useState<MentionSuggestion[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  useEffect(() => {
    setMentions(initialMentions);
  }, [initialMentions]);

  useEffect(() => {
    let cancelled = false;

    const fetchSuggestions = async (query: string) => {
      setLoadingSuggestions(true);
      try {
        const results = await suggestMentions(query);
        if (!cancelled) {
          setSuggestions(results);
        }
      } catch {
        if (!cancelled) {
          setSuggestions([]);
        }
      } finally {
        if (!cancelled) {
          setLoadingSuggestions(false);
        }
      }
    };

    if (mentionContext && mentionContext.query.length >= MIN_MENTION_QUERY) {
      void fetchSuggestions(mentionContext.query);
    } else {
      setSuggestions([]);
    }

    return () => {
      cancelled = true;
    };
  }, [mentionContext]);

  const handleValueChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const nextValue = event.target.value;
    setValue(nextValue);
    setSubmitError(null);

    const caret = event.target.selectionStart ?? nextValue.length;
    const textBeforeCaret = nextValue.slice(0, caret);
    const match = textBeforeCaret.match(/@([A-Za-z0-9._-]{1,50})$/);

    if (match) {
      const start = caret - match[0].length;
      const end = caret;
      const query = match[1];
      setMentionContext({ start, end, query });
    } else if (mentionContext) {
      setMentionContext(null);
    }
  };

  const handleMentionSelect = (suggestion: MentionSuggestion) => {
    if (!mentionContext) {
      return;
    }

    const before = value.slice(0, mentionContext.start);
    const after = value.slice(mentionContext.end);
    const labelText = suggestion.displayName ?? suggestion.userId;
    const insertion = `@${labelText} `;

    setValue(`${before}${insertion}${after}`);
    setMentionContext(null);
    setSuggestions([]);

    setMentions((current) => {
      if (current.some((mention) => mention.userId === suggestion.userId)) {
        return current;
      }

      return [
        ...current,
        {
          userId: suggestion.userId,
          displayName: suggestion.displayName,
          email: suggestion.email,
          avatarUrl: suggestion.avatarUrl,
        },
      ];
    });
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) {
      setSubmitError('Please enter a comment before submitting.');
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      await onSubmit({
        content: trimmed,
        mentions,
      });
      setValue('');
      setMentions([]);
      setMentionContext(null);
      setSuggestions([]);
    } catch {
      setSubmitError('Unable to submit the comment right now. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    setValue(initialValue);
    setMentions(initialMentions);
    setMentionContext(null);
    setSuggestions([]);
    setSubmitError(null);
    onCancel?.();
  };

  return (
    <form onSubmit={handleSubmit} className="comment-composer">
      <div className="comment-composer__field">
        <label htmlFor={id}>{label}</label>
        <textarea
          id={id}
          value={value}
          onChange={handleValueChange}
          placeholder={placeholder}
          aria-label={label}
          rows={4}
          autoFocus={autoFocus}
        />
      </div>

      {loadingSuggestions && (
        <p role="status">Loading mention suggestions…</p>
      )}

      {!loadingSuggestions && suggestions.length > 0 && (
        <ul role="listbox" className="comment-composer__mentions">
          {suggestions.map((suggestion) => (
            <li key={suggestion.userId}>
              <button
                type="button"
                role="option"
                onClick={() => handleMentionSelect(suggestion)}
              >
                {suggestion.displayName ?? suggestion.userId}
                {suggestion.email ? <span> ({suggestion.email})</span> : null}
              </button>
            </li>
          ))}
        </ul>
      )}

      {submitError && (
        <p role="alert" className="comment-composer__error">
          {submitError}
        </p>
      )}

      <div className="comment-composer__actions">
        <button type="submit" disabled={submitting}>
          {submitLabel}
        </button>
        {onCancel && (
          <button type="button" onClick={handleCancel} disabled={submitting}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

type CommentItemProps = {
  comment: Comment;
  canEdit: boolean;
  isEditing: boolean;
  onEdit: () => void;
  onDelete: () => void;
  renderEditor: () => React.ReactNode;
};

const CommentItem = ({
  comment,
  canEdit,
  isEditing,
  onEdit,
  onDelete,
  renderEditor,
}: CommentItemProps) => {
  return (
    <div className="comment-item" data-testid={`comment-${comment.id}`}>
      <div className="comment-item__meta">
        <strong>{comment.authorName}</strong>{' '}
        <span className="comment-item__timestamp">{formatTimestamp(comment.createdAt)}</span>
        {comment.isEdited && <span className="comment-item__edited"> (edited)</span>}
      </div>

      {!isEditing && (
        <p className="comment-item__content">{comment.content}</p>
      )}

      {isEditing ? (
        renderEditor()
      ) : (
        canEdit && (
          <div className="comment-item__actions">
            <button type="button" onClick={onEdit} aria-label="Edit comment">
              Edit comment
            </button>
            <button type="button" onClick={onDelete} aria-label="Delete comment">
              Delete comment
            </button>
          </div>
        )
      )}
    </div>
  );
};

const CommentThread = ({ entityType, entityId, currentUser }: CommentThreadProps) => {
  const { modalState, showConfirm, closeModal } = useModal();
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeEditId, setActiveEditId] = useState<string | null>(null);

  const refreshComments = useCallback(async () => {
    const data = await listComments({ entityType, entityId });
    if (Array.isArray(data)) {
      setComments(normaliseComments(data));
    } else {
      setComments([]);
    }
  }, [entityId, entityType]);

  const initialise = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await refreshComments();
    } catch {
      setError('Unable to load comments right now. Please try again later.');
      setComments([]);
    } finally {
      setLoading(false);
    }
  }, [refreshComments]);

  useEffect(() => {
    void initialise();
  }, [initialise]);

  const handleCreateComment = async ({ content, mentions }: ComposerSubmitPayload) => {
    await createComment({
      entityType,
      entityId,
      content,
      mentions,
      parentCommentId: null,
    });
    await refreshComments();
  };

  const handleEditComment = async (commentId: string, { content, mentions }: ComposerSubmitPayload) => {
    await updateComment({
      commentId,
      content,
      mentions,
    });
    await refreshComments();
    setActiveEditId(null);
  };

  const handleDeleteComment = async (commentId: string) => {
    showConfirm(
      'Delete this comment? This action cannot be undone.',
      async () => {
        await deleteComment({ commentId });
        await refreshComments();
      },
      {
        title: 'Delete Comment',
        confirmText: 'Delete',
        cancelText: 'Cancel',
      }
    );
  };

  const renderComment = (comment: Comment): React.ReactNode => {
    const isEditing = activeEditId === comment.id;
    const canEdit = comment.authorId === currentUser.id;

    return (
      <div key={comment.id} className="comment-thread__item">
        <CommentItem
          comment={comment}
          canEdit={canEdit}
          isEditing={isEditing}
          onEdit={() => setActiveEditId(comment.id)}
          onDelete={() => {
            handleDeleteComment(comment.id).catch(() => {
              setError('Failed to delete the comment. Please try again.');
            });
          }}
          renderEditor={() => (
            <CommentComposer
              id={`edit-comment-${comment.id}`}
              label="Edit your comment"
              submitLabel="Save changes"
              initialValue={comment.content}
              initialMentions={comment.mentions ?? []}
              autoFocus
              onCancel={() => setActiveEditId(null)}
              onSubmit={async (payload) => {
                await handleEditComment(comment.id, payload);
              }}
            />
          )}
        />

        <div data-testid={`comment-replies-${comment.id}`} className="comment-thread__replies">
          {comment.replies.length > 0 &&
            comment.replies.map((reply) => (
              <div key={reply.id} className="comment-thread__reply">
                {renderComment(reply)}
              </div>
            ))}
        </div>
      </div>
    );
  };

  const hasComments = comments.length > 0;

  return (
    <section className="comment-thread">
      <header>
        <h2>Comments</h2>
      </header>

      {error && (
        <p role="alert" className="comment-thread__error">
          {error}
        </p>
      )}

      {loading ? (
        <p>Loading comments…</p>
      ) : hasComments ? (
        <div className="comment-thread__list">
          {comments.map((comment) => renderComment(comment))}
        </div>
      ) : (
        <p className="comment-thread__empty">No comments yet. Start the discussion below.</p>
      )}

      <CommentComposer
        id="new-comment"
        label="Add a comment"
        placeholder="Share your feedback or ask a question…"
        submitLabel="Post comment"
        onSubmit={handleCreateComment}
      />

      {/* Modal for confirmations */}
      <Modal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        onConfirm={modalState.onConfirm}
        title={modalState.title}
        message={modalState.message}
        type={modalState.type}
        confirmText={modalState.confirmText}
        cancelText={modalState.cancelText}
        showCancel={modalState.showCancel}
      />
    </section>
  );
};

export default CommentThread;
