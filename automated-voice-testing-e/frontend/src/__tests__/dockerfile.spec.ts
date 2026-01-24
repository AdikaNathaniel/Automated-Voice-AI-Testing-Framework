// @vitest-environment node

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

// TODO: Create frontend/Dockerfile before enabling these tests
describe.skip('Frontend Dockerfile', () => {
  const dockerfilePath = resolve(__dirname, '../../Dockerfile');
  const contents = readFileSync(dockerfilePath, 'utf-8');

  it('runs the optimized production build', () => {
    expect(contents).toMatch(/npm run build/);
  });

  it('serves via nginx stage', () => {
    expect(contents).toMatch(/FROM nginx:alpine/);
    expect(contents).toMatch(/COPY --from=builder \/app\/dist \/usr\/share\/nginx\/html/);
  });
});
