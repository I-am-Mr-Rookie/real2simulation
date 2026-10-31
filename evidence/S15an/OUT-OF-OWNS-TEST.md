# S15an: one out-of-Owns test needs a one-line update at merge

`tests/web-private/public-chrome.test.mjs` (owned by S15ao) asserts the removed native select:

```js
assert.match(toggle, /THEME_OPTIONS\.map\(\(o\) => <option key=\{o\.id\} value=\{o\.id\}>/);
```

S15an (b) replaced that select with the single swatch menu, so this line fails (1/159). Proposed replacement (same intent: every mode listed):

```js
assert.match(toggle, /THEME_OPTIONS\.map\(\(t\) => <button key=\{t\.id\} type="button" data-theme-option=\{t\.id\}/);
```

Not applied here: the file is outside S15an Owns and no controller-messaging tool was available in this worker.
