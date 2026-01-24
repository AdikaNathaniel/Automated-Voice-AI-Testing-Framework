import { describe, expect, it } from 'vitest';

import * as commentService from '../../../services/comment.service';

describe('comment service import', () => {
  it('exposes helpers', () => {
    expect(commentService).toBeDefined();
  });
});
