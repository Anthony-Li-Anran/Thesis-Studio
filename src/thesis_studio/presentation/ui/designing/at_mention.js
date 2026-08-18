
        (function() {
          var menu = null, atPos = -1, filter = '', activeInput = null;
          function getMenu() {
            if (menu) return menu;
            menu = document.createElement('div');
            menu.id = 'ts-at-menu';
            document.body.appendChild(menu);
            menu.addEventListener('click', function(e) {
              var item = e.target.closest('.ts-at-item');
              if (!item || !activeInput) return;
              var agent = item.getAttribute('data-at') || '';
              var val = activeInput.value;
              activeInput.value = val.substring(0, atPos) + '@' + agent + ' ' + val.substring(activeInput.selectionStart);
              activeInput.focus();
              activeInput.dispatchEvent(new Event('input', {bubbles: true}));
              menu.style.display = 'none';
            });
            return menu;
          }
          function bindInput(inp) {
            if (inp.hasAttribute('data-ts-at')) return;
            inp.setAttribute('data-ts-at', '1');
            inp.addEventListener('input', function() {
              var val = this.value, pos = this.selectionStart;
              var lastAt = -1;
              for (var i = pos - 1; i >= 0; i--) {
                if (val[i] === '@') { lastAt = i; break; }
                if (val[i] === ' ' || val[i] === '\\n') break;
              }
              if (lastAt >= 0) {
                activeInput = this; atPos = lastAt; filter = val.substring(lastAt + 1, pos).toLowerCase();
                var m = getMenu();
                m.innerHTML = [
                  '<div class="ts-at-item" data-at="all">@all - All Agents</div>',
                  '<div class="ts-at-divider"></div>',
                  '<div class="ts-at-item" data-at="Researcher"><span class="ts-at-dot" style="background:#2563eb"></span>@Researcher</div>',
                  '<div class="ts-at-item" data-at="Debater"><span class="ts-at-dot" style="background:#7c3aed"></span>@Debater</div>',
                  '<div class="ts-at-item" data-at="Reviewer"><span class="ts-at-dot" style="background:#db2777"></span>@Reviewer</div>'
                ].join('');
                var rect = this.getBoundingClientRect();
                m.style.display = 'block';
                m.style.visibility = 'hidden';
                var menuH = m.offsetHeight;
                m.style.visibility = 'visible';
                var top = rect.top - menuH - 6;
                if (top < 8) top = rect.bottom + 6;
                m.style.left = rect.left + 'px';
                m.style.top = top + 'px';
                var vis = false;
                m.querySelectorAll('.ts-at-item').forEach(function(it) {
                  var t = (it.getAttribute('data-at') || '').toLowerCase();
                  if (t.indexOf(filter) >= 0) { it.style.display = 'flex'; vis = true; }
                  else { it.style.display = 'none'; }
                });
                if (!vis) m.style.display = 'none';
              } else {
                if (menu) menu.style.display = 'none';
              }
            });
            inp.addEventListener('keydown', function(e) {
              if (e.key === 'Escape' && menu) { menu.style.display = 'none'; e.preventDefault(); }
            });
            inp.addEventListener('blur', function() {
              setTimeout(function() { if (menu) menu.style.display = 'none'; }, 200);
            });
          }
          var obs = new MutationObserver(function() {
            document.querySelectorAll('input:not([data-ts-at])').forEach(bindInput);
          });
          obs.observe(document.body, {childList: true, subtree: true});
          document.querySelectorAll('input:not([data-ts-at])').forEach(bindInput);
          document.addEventListener('click', function(e) {
            if (menu && !menu.contains(e.target) && e.target !== activeInput) menu.style.display = 'none';
          });
        })();
        