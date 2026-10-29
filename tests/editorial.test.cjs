const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../site/assets/js/editorial.js'), 'utf8');

function fixture({ reduced = false, blockedStorage = false, saved = null, clipboardFails = false } = {}) {
  const events = {};
  const root = { dataset: {}, scrollHeight: 5000 };
  const motion = { hidden: true, addEventListener: (name, fn) => events.motion = fn, setAttribute: (key, value) => motion[key] = value };
  const copy = { hidden: true, dataset: { copyEmail: 'parsa.emm@gmail.com' }, addEventListener: (name, fn) => events.copy = fn };
  const status = {};
  const media = { matches: reduced, addEventListener: (name, fn) => events.media = fn };
  const title = { style: {}, getBoundingClientRect: () => ({ top: 250 }) };
  const copied = [];
  let stored = saved;
  const context = vm.createContext({
    document: {
      documentElement: root,
      querySelector: selector => ({ '[data-motion-toggle]': motion, '[data-copy-email]': copy, '[data-copy-status]': status }[selector] || null),
      querySelectorAll: () => [title]
    },
    localStorage: {
      getItem: () => { if (blockedStorage) throw Error('blocked'); return stored; },
      setItem: (key, value) => { if (blockedStorage) throw Error('blocked'); stored = value; }
    },
    matchMedia: query => query.includes('reduced') ? media : { matches: true, addEventListener: () => {} },
    window: { innerHeight: 900, scrollY: 100, addEventListener: (name, fn) => events[name] = fn },
    navigator: { clipboard: { writeText: async value => { if (clipboardFails) throw Error('denied'); copied.push(value); } } },
    requestAnimationFrame: () => 1,
    cancelAnimationFrame: () => {},
    setInterval: () => {}
  });
  vm.runInContext(source, context);
  return { root, motion, copy, status, media, events, copied, stored: () => stored };
}

test('OS reduced motion wins over a stored play preference and clears transforms', () => {
  const f = fixture({ reduced: true, saved: 'playing' });
  assert.equal(f.root.dataset.motion, 'paused');
  assert.equal(f.motion.disabled, true);
  assert.equal(f.motion.textContent, 'Reduced motion');
  f.media.matches = false;
  f.events.media();
  assert.equal(f.root.dataset.motion, 'playing');
  assert.equal(f.motion.disabled, false);
});

test('motion can be paused and resumed when storage is blocked', () => {
  const f = fixture({ blockedStorage: true });
  f.events.motion();
  assert.equal(f.root.dataset.motion, 'paused');
  assert.equal(f.motion['aria-pressed'], 'true');
  f.events.motion();
  assert.equal(f.root.dataset.motion, 'playing');
});

test('motion preference persists and can be reset from another tab', () => {
  const f = fixture({ saved: 'paused' });
  assert.equal(f.root.dataset.motion, 'paused');
  f.events.motion();
  assert.equal(f.stored(), 'playing');
  f.events.storage({ key: 'profile-motion', newValue: 'paused' });
  assert.equal(f.root.dataset.motion, 'paused');
  f.events.storage({ key: null, newValue: null });
  assert.equal(f.root.dataset.motion, 'playing');
});

test('successful copy announces completion and restores the button', async () => {
  const f = fixture();
  await f.events.copy();
  assert.deepEqual(f.copied, ['parsa.emm@gmail.com']);
  assert.equal(f.status.textContent, 'Email copied.');
  assert.equal(f.copy.disabled, false);
});

test('denied clipboard access provides a useful fallback without a false success', async () => {
  const f = fixture({ clipboardFails: true });
  await f.events.copy();
  assert.match(f.status.textContent, /Select the email address/);
  assert.equal(f.copy.disabled, false);
  assert.equal(f.copied.length, 0);
});
