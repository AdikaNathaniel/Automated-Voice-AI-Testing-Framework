import { act, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import ActivityFeed from '../ActivityFeed';
import type { ActivityFeed as ActivityFeedResponse } from '../../../types/activity';

const mockGetActivityFeed = vi.fn();
const mockOn = vi.fn();
const mockOff = vi.fn();

vi.mock('../../../services/activity.service', () => ({
  getActivityFeed: (...args: unknown[]) => mockGetActivityFeed(...args),
}));

vi.mock('../../../services/websocket.service', () => ({
  __esModule: true,
  default: {
    on: (...args: unknown[]) => mockOn(...args),
    off: (...args: unknown[]) => mockOff(...args),
  },
}));

const createFeed = (overrides?: Partial<ActivityFeedResponse>): ActivityFeedResponse => ({
  items: [
    {
      id: 'event-1',
      userId: 'user-123',
      actionType: 'test_case.created',
      resourceType: 'test_case',
      resourceId: 'case-456',
      actionDescription: 'Created test case',
      metadata: {
        summary: 'Initial test case creation',
      },
      ipAddress: '192.168.0.10',
      createdAt: '2025-03-15T10:00:00Z',
    },
  ],
  pagination: {
    limit: 25,
    offset: 0,
    returned: 1,
    userId: null,
    actionType: null,
    resourceType: null,
    since: null,
  },
  ...overrides,
});

describe('ActivityFeed component', () => {
  beforeEach(() => {
    mockGetActivityFeed.mockReset();
    mockOn.mockReset();
    mockOff.mockReset();
  });

  it('renders activity entries returned by the service', async () => {
    mockGetActivityFeed.mockResolvedValueOnce(createFeed());

    render(<ActivityFeed />);

    expect(mockGetActivityFeed).toHaveBeenCalledWith({
      limit: 25,
      offset: 0,
    });

    const items = await screen.findAllByRole('listitem');

    expect(items).toHaveLength(1);
    expect(within(items[0]).getByText(/Created test case/i)).toBeInTheDocument();
    expect(within(items[0]).getByText(/test_case\.created/i)).toBeInTheDocument();
    expect(within(items[0]).getByText(/Initial test case creation/i)).toBeInTheDocument();
  });

  it('applies user and action filters when requested', async () => {
    mockGetActivityFeed.mockResolvedValueOnce(createFeed());
    mockGetActivityFeed.mockResolvedValueOnce(
      createFeed({
        items: [],
        pagination: {
          limit: 25,
          offset: 0,
          returned: 0,
          userId: 'user-222',
          actionType: 'validation.reviewed',
          resourceType: null,
          since: null,
        },
      })
    );

    render(<ActivityFeed />);

    await screen.findByText(/Created test case/i);

    const user = await userEvent.setup();

    await user.type(screen.getByLabelText(/Filter by user/i), 'user-222');
    await user.type(screen.getByLabelText(/Action type/i), 'validation.reviewed');
    await user.click(screen.getByRole('button', { name: /Apply Filters/i }));

    await waitFor(() => {
      expect(mockGetActivityFeed).toHaveBeenNthCalledWith(2, {
        limit: 25,
        offset: 0,
        userId: 'user-222',
        actionType: 'validation.reviewed',
      });
    });

    expect(
      screen.getByText(/No activity events match the selected filters\. Try adjusting your criteria\./i)
    ).toBeInTheDocument();
  });

  it('prepends real-time activity events when they match active filters', async () => {
    mockGetActivityFeed.mockResolvedValueOnce(createFeed());

    let activityHandler: ((data: ActivityFeedResponse['items'][number]) => void) | undefined;

    mockOn.mockImplementation((event: string, handler: (data: unknown) => void) => {
      if (event === 'activity:created') {
        activityHandler = handler as (data: ActivityFeedResponse['items'][number]) => void;
      }
    });

    render(<ActivityFeed />);

    await screen.findByText(/Created test case/i);
    expect(activityHandler).toBeDefined();

    act(() => {
      activityHandler?.({
        id: 'event-2',
        userId: 'user-123',
        actionType: 'test_case.created',
        resourceType: 'test_case',
        resourceId: 'case-789',
        actionDescription: 'Updated test case',
        metadata: {
          summary: 'Real-time update',
        },
        ipAddress: '127.0.0.1',
        createdAt: '2025-03-15T11:00:00Z',
      });
    });

    const entries = await screen.findAllByRole('listitem');
    expect(entries).toHaveLength(2);
    expect(within(entries[0]).getByText(/Updated test case/i)).toBeInTheDocument();
    expect(within(entries[1]).getByText(/Created test case/i)).toBeInTheDocument();
  });

  it('unsubscribes from the real-time channel when unmounted', async () => {
    mockGetActivityFeed.mockResolvedValueOnce(createFeed());

    let activityHandler: ((data: ActivityFeedResponse['items'][number]) => void) | undefined;

    mockOn.mockImplementation((event: string, handler: (data: unknown) => void) => {
      if (event === 'activity:created') {
        activityHandler = handler as (data: ActivityFeedResponse['items'][number]) => void;
      }
    });

    const { unmount } = render(<ActivityFeed />);

    await screen.findByText(/Created test case/i);

    unmount();

    expect(mockOff).toHaveBeenCalledWith('activity:created', activityHandler);
  });
});
