import test from 'node:test';
import assert from 'node:assert/strict';
import {ageLabel} from '../docs/satellite.js';
test('snapshots expose old and invalid timestamps', () => {
  const now=Date.parse('2026-10-30T12:00:00Z');
  assert.match(ageLabel('2026-10-28T12:00:00Z',now),/refresh recommended/);
  assert.equal(ageLabel('2026-10-30T06:00:00Z',now),'6.0 hours old');
  assert.match(ageLabel('2026-11-01T00:00:00Z',now),/review/);
  assert.match(ageLabel('unknown',now),/review/);
});
