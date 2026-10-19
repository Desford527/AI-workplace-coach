/* Load before CSS to restore the chosen theme without a color flash. */
(() => {
  'use strict';
  const themes = [
    {id:'corporate', name:'企业红', note:'默认 · PPT 同款中车红与岩灰', colors:['#ffffff','#c70019','#4c4948']},
    {id:'forest', name:'纸色深绿', note:'熟悉的纸色、深绿与青柠', colors:['#f4f1e9','#174f40','#d7ef7b']},
    {id:'ocean', name:'晴空蓝', note:'清爽蓝白，适合专注工作', colors:['#f2f6fa','#164c72','#bce8ec']},
    {id:'violet', name:'雾紫', note:'柔和紫灰，给练习一点松弛', colors:['#f6f2f8','#57416f','#e2d4ef']}
  ];
  const key = 'workplace_theme';
  let current = themes[0];
  const apply = id => {
    current = themes.find(t => t.id === id) || themes[0];
    document.documentElement.dataset.theme = current.id;
    return current;
  };
  try { apply(localStorage.getItem(key)); } catch { apply('corporate'); }
  window.CoachTheme = {
    themes,
    get current() { return current; },
    set(id) {
      const theme = apply(id);
      try { localStorage.setItem(key, theme.id); } catch { /* Session selection still works. */ }
      return theme;
    }
  };
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      apply(event.newValue);
      window.dispatchEvent(new Event('coach-theme-change'));
    }
  });
})();
