const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');

function fixture({ stored = null, dark = false, blocked = false } = {}) {
  const listeners = {};
  const source = { srcset: 'assets/art/study-attestara-dark.svg' };
  const image = { dataset: { themed: 'assets/art/study-attestara' }, parentElement: { querySelector: () => source } };
  const control = { hidden: true, addEventListener: (name, fn) => listeners[name] = fn, setAttribute: (key, value) => control[key] = value };
  const label = {};
  const html = { dataset: {} };
  const media = { matches: dark, addEventListener: (name, fn) => listeners.media = fn };
  let value = stored;
  const context = vm.createContext({
    document: { documentElement: html, querySelector: selector => selector === '.theme-toggle' ? control : label, querySelectorAll: () => [image] },
    localStorage: {
      getItem: () => { if (blocked) throw Error('blocked'); return value; },
      setItem: (key, next) => { if (blocked) throw Error('blocked'); value = next; },
      removeItem: () => { if (blocked) throw Error('blocked'); value = null; }
    },
    matchMedia: () => media,
    window: { addEventListener: (name, fn) => listeners[name] = fn }
  });
  for (const file of ['theme-init.js', 'app.js']) {
    vm.runInContext(fs.readFileSync(path.join(root, 'site/assets/js', file), 'utf8'), context);
  }
  return { html, control, label, media, image, source, listeners, stored: () => value };
}

test('system follows the OS and applies matching artwork', () => {
  const f = fixture({ dark: true });
  assert.equal(f.control.hidden, false);
  assert.equal(f.label.textContent, 'System');
  assert.equal(f.html.dataset.theme, undefined);
  assert.match(f.image.src, /-dark.svg$/);
  f.media.matches = false;
  f.listeners.media();
  assert.match(f.source.srcset, /-light.svg$/);
});

test('explicit preference survives startup and overrides the OS', () => {
  const f = fixture({ stored: 'light', dark: true });
  assert.equal(f.html.dataset.theme, 'light');
  assert.match(f.image.src, /-light.svg$/);
  f.listeners.click();
  assert.equal(f.html.dataset.theme, 'dark');
  assert.equal(f.stored(), 'dark');
  assert.match(f.source.srcset, /-dark.svg$/);
  f.listeners.click();
  assert.equal(f.html.dataset.theme, undefined);
  assert.equal(f.stored(), null);
  assert.equal(f.label.textContent, 'System');
});

test('blocked storage still allows switching the visible theme', () => {
  const f = fixture({ blocked: true });
  f.listeners.click();
  assert.equal(f.html.dataset.theme, 'light');
  f.listeners.click();
  assert.equal(f.html.dataset.theme, 'dark');
  assert.match(f.control['aria-label'], /Switch to system mode/);
});

test('another tab can reset the preference to system', () => {
  const f = fixture({ stored: 'dark' });
  f.listeners.storage({ key: 'profile-theme', newValue: 'light' });
  assert.equal(f.html.dataset.theme, 'light');
  f.listeners.storage({ key: null, newValue: null });
  assert.equal(f.label.textContent, 'System');
  assert.equal(f.html.dataset.theme, undefined);
});
