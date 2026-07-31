"""Prism dark theme homepage: project list (desktop only)."""

from nicegui import ui

from .theme import apply_theme, logo

_SEARCH_INPUT = (
    "ts-text-editor-primary ts-bg-input ts-border-input ts-search-input "
    "flex grow w-full py-2 pl-12 text-sm shadow-xs border rounded-full"
)

_SEARCH_ICON = (
    '<svg fill="currentColor" width="22" height="22" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" class="ts-text-editor-tertiary">'
    '<path d="M14.0859 8.74999C14.0859 5.80355 11.6974 3.41503 8.75098 '
    "3.41503C5.80454 3.41503 3.41602 5.80355 3.41602 8.74999C3.41602 "
    "11.6964 5.80454 14.085 8.75098 14.085C11.6974 14.085 14.0859 "
    "11.6964 14.0859 8.74999ZM15.416 8.74999C15.416 10.3539 14.8482 "
    "11.8245 13.9043 12.9746L13.9707 13.0303L16.9707 16.0303L17.0566 "
    "16.1338C17.2271 16.3919 17.1979 16.7434 16.9707 16.9707C16.7434 "
    "17.1975 16.3927 17.226 16.1347 17.0557L16.0302 16.9707L13.0302 "
    "13.9707L12.9755 13.9033C11.8255 14.8472 10.3549 15.415 8.75098 "
    "15.415C5.07 15.415 2.08594 12.431 2.08594 8.74999C2.08594 5.06901 "
    "5.07 2.08495 8.75098 2.08495C12.4319 2.08495 15.416 5.06901 15.416 "
    '8.74999Z"></path></svg>'
)

_CHEVRON_DOWN = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M15.2792 7.52929C15.5389 7.26959 15.9609 7.26959 16.2206 '
    "7.52929C16.4803 7.78898 16.4803 8.21099 16.2206 8.47069L10.4706 "
    "14.2207C10.2109 14.4804 9.78884 14.4804 9.52914 14.2207L3.77914 "
    "8.47069L3.69418 8.3662C3.52367 8.10807 3.55187 7.75655 3.77914 "
    "7.52929C4.00641 7.30202 4.35792 7.27382 4.61605 7.44433L4.72055 "
    '7.52929L9.99984 12.8086L15.2792 7.52929Z"></path></svg>'
)

_CHEVRON_UP_DOWN = (
    '<svg fill="none" viewBox="0 0 20 20" stroke-width="1.5" '
    'stroke="currentColor" width="16" height="16" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" '
    'class="shrink-0">'
    '<path stroke-linecap="round" stroke-linejoin="round" '
    'd="M5.5 8L10 3.5L14.5 8"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" '
    'd="M5.5 12L10 16.5L14.5 12"/>'
    "</svg>"
)

_PLUS_ICON = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M9.33496 16.5V10.665H3.5C3.13273 10.665 2.83496 10.3673 '
    "2.83496 10C2.83496 9.63273 3.13273 9.33496 3.5 9.33496H9.33496V3.5"
    "C9.33496 3.13273 9.63273 2.83496 10 2.83496C10.3673 2.83496 10.665 "
    "3.13273 10.665 3.5V9.33496H16.5L16.6338 9.34863C16.9369 9.41057 "
    "17.165 9.67857 17.165 10C17.165 10.3214 16.9369 10.5894 16.6338 "
    "10.6514L16.5 10.665H10.665V16.5C10.665 16.8673 10.3673 17.165 10 "
    '17.165C9.63273 17.165 9.33496 16.8673 9.33496 16.5Z"></path></svg>'
)

_SIDEBAR_TOGGLE_ICON = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M6.835 4C6.383 4.004 6.014 4.012 5.698 4.038C5.312 4.070 '
    "5.039 4.123 4.822 4.200L4.622 4.286C4.183 4.510 3.815 4.850 3.559 "
    "5.268L3.456 5.452C3.330 5.699 3.250 6.014 3.208 6.528C3.165 7.051 "
    "3.165 7.719 3.165 8.663V11.327C3.165 12.271 3.165 12.939 3.208 "
    "13.462C3.250 13.977 3.330 14.291 3.456 14.538L3.559 14.722C3.815 "
    "15.140 4.183 15.480 4.622 15.704L4.822 15.790C5.039 15.867 5.312 "
    "15.921 5.698 15.952C6.014 15.978 6.383 15.986 6.834 15.990V4ZM18.165 "
    "11.327C18.165 12.249 18.165 12.981 18.117 13.570C18.075 14.092 "
    "17.992 14.547 17.813 14.965L17.730 15.142C17.394 15.800 16.883 "
    "16.351 16.257 16.735L15.981 16.890C15.516 17.127 15.007 17.229 "
    "14.410 17.277C13.821 17.325 13.089 17.325 12.167 17.325H7.833"
    "C6.911 17.325 6.179 17.325 5.590 17.277C5.068 17.235 4.613 17.151 "
    "4.195 16.972L4.019 16.890C3.360 16.554 2.809 16.043 2.425 15.417"
    "L2.271 15.142C2.033 14.676 1.932 14.167 1.883 13.570C1.835 12.981 "
    "1.835 12.249 1.835 11.327V8.663C1.835 7.741 1.835 7.009 1.883 "
    "6.420C1.932 5.823 2.033 5.314 2.271 4.849L2.425 4.573C2.809 3.947 "
    "3.360 3.436 4.019 3.101L4.195 3.018C4.613 2.838 5.068 2.755 5.590 "
    "2.713C6.179 2.665 6.911 2.665 7.833 2.665H12.167C13.089 2.665 13.821 "
    "2.665 14.410 2.713C15.007 2.762 15.516 2.863 15.981 3.101L16.257 "
    "3.255C16.883 3.639 17.394 4.190 17.730 4.849L17.813 5.025C17.992 "
    "5.443 18.075 5.898 18.117 6.420C18.165 7.009 18.165 7.741 18.165 "
    "8.663V11.327ZM8.164 15.995H12.167C13.111 15.995 13.779 15.995 14.302 "
    "15.952C14.816 15.910 15.131 15.830 15.378 15.704L15.562 15.602"
    "C15.980 15.345 16.320 14.977 16.544 14.538L16.630 14.338C16.707 "
    "14.121 16.761 13.848 16.792 13.462C16.835 12.939 16.835 12.271 16.835 "
    "11.327V8.663C16.835 7.719 16.835 7.051 16.792 6.528C16.761 6.142 "
    "16.707 5.869 16.630 5.652L16.544 5.452C16.320 5.013 15.980 4.645 "
    "15.562 4.389L15.378 4.286C15.131 4.160 14.817 4.080 14.302 4.038"
    'C13.779 3.995 13.111 3.995 12.167 3.995H8.164V15.995Z"></path>'
    "</svg>"
)


_LIST_ICON = (
    '<svg fill="currentColor" width="20" height="20" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" '
    'class="shrink-0">'
    '<path d="M5.69336 11.0557C7.05891 11.1944 8.12484 12.3479 8.125 '
    "13.75L8.11035 14.0273C7.97144 15.3928 6.81814 16.459 5.41602 "
    "16.459L5.13965 16.4443C3.86514 16.3149 2.85128 15.3018 2.72168 "
    "14.0273L2.70801 13.75C2.70818 12.2546 3.92061 11.0423 5.41602 "
    "11.042L5.69336 11.0557ZM5.41602 12.3721C4.65515 12.3724 4.03826 "
    "12.9891 4.03809 13.75C4.03826 14.5109 4.65515 15.1286 5.41602 "
    "15.1289C6.17714 15.1289 6.79475 14.5111 6.79492 13.75C6.79475 "
    '12.9889 6.17714 12.3721 5.41602 12.3721Z"></path>'
    '<path d="M16.8008 13.0986C17.1036 13.1608 17.3311 13.4288 17.3311 '
    "13.75C17.3311 14.0712 17.1036 14.3392 16.8008 14.4014L16.666 "
    "14.415H10.833C10.4659 14.4149 10.168 14.1172 10.168 13.75C10.168 "
    '13.3828 10.4659 13.0851 10.833 13.085H16.666L16.8008 13.0986Z"></path>'
    '<path d="M5.69336 3.55566C7.05891 3.69438 8.12484 4.84789 8.125 '
    "6.25L8.11035 6.52734C7.97144 7.89281 6.81814 8.95898 5.41602 "
    "8.95898L5.13965 8.94434C3.86514 8.81489 2.85128 7.80181 2.72168 "
    "6.52734L2.70801 6.25C2.70818 4.75457 3.92061 3.5423 5.41602 "
    "3.54199L5.69336 3.55566ZM5.41602 4.87207C4.65515 4.87238 4.03826 "
    "5.48911 4.03809 6.25C4.03826 7.0109 4.65515 7.6286 5.41602 "
    "7.62891C6.17714 7.62891 6.79475 7.01109 6.79492 6.25C6.79475 "
    '5.48892 6.17714 4.87207 5.41602 4.87207Z"></path>'
    '<path d="M16.8008 5.59863C17.1036 5.66081 17.3311 5.92879 17.3311 '
    "6.25C17.3311 6.57121 17.1036 6.83919 16.8008 6.90137L16.666 "
    "6.91504H10.833C10.4659 6.91491 10.168 6.61719 10.168 6.25C10.168 "
    '5.88281 10.4659 5.58509 10.833 5.58496H16.666L16.8008 5.59863Z"></path>'
    "</svg>"
)

_GRID_ICON = (
    '<svg fill="currentColor" width="20" height="20" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M4.49805 3.50159C5.32544 3.50159 5.99689 4.17228 5.99707 '
    "4.99963C5.99707 5.8271 5.32555 6.4987 4.49805 6.4987C3.67069 6.4985 "
    '3 5.827 3 4.99963C3.00018 4.17239 3.6708 3.50176 4.49805 3.50159Z"></path>'
    '<path d="M9.83102 3.50159C10.6583 3.50176 11.3289 4.17239 11.3291 '
    "4.99963C11.3291 5.827 10.6584 6.4985 9.83102 6.4987C9.00355 6.4987 "
    "8.33203 5.8271 8.33203 4.99963C8.33221 4.17228 9.00366 3.50159 "
    '9.83102 3.50159Z"></path>'
    '<path d="M15.1621 3.50159C15.9895 3.50159 16.66 4.17228 16.6602 '
    "4.99963C16.6602 5.8271 15.9897 6.4987 15.1621 6.4987C14.3346 6.4987 "
    "13.6641 5.8271 13.6641 4.99963C13.6642 4.17228 14.3346 3.50159 "
    '15.1621 3.50159Z"></path>'
    '<path d="M4.49805 8.83447C5.32544 8.83447 5.99689 9.50516 5.99707 '
    "10.3325C5.99707 11.16 5.32555 11.8316 4.49805 11.8316C3.67069 "
    "11.8314 3 11.1599 3 10.3325C3.00018 9.50526 3.6708 8.83463 4.49805 "
    '8.83447Z"></path>'
    '<path d="M9.83102 8.83447C10.6583 8.83463 11.3289 9.50526 11.3291 '
    "10.3325C11.3291 11.1599 10.6584 11.8314 9.83102 11.8316C9.00355 "
    "11.8316 8.33203 11.16 8.33203 10.3325C8.33221 9.50516 9.00366 "
    '8.83447 9.83102 8.83447Z"></path>'
    '<path d="M15.1621 8.83447C15.9895 8.83447 16.66 9.50516 16.6602 '
    "10.3325C16.6602 11.16 15.9897 11.8316 15.1621 11.8316C14.3346 "
    "11.8316 13.6641 11.16 13.6641 10.3325C13.6642 9.50516 14.3346 "
    '8.83447 15.1621 8.83447Z"></path>'
    '<path d="M4.49805 14.5015C5.32544 14.5015 5.99689 15.1722 5.99707 '
    "15.9996C5.99707 16.8271 5.32555 17.4987 4.49805 17.4987C3.67069 "
    "17.4985 3 16.827 3 15.9996C3.00018 15.1724 3.6708 14.5018 4.49805 "
    '14.5015Z"></path>'
    '<path d="M9.83102 14.5015C10.6583 14.5018 11.3289 15.1724 11.3291 '
    "15.9996C11.3291 16.827 10.6584 17.4985 9.83102 17.4987C9.00355 "
    "17.4987 8.33203 16.8271 8.33203 15.9996C8.33221 15.1722 9.00366 "
    '14.5015 9.83102 14.5015Z"></path>'
    '<path d="M15.1621 14.5015C15.9895 14.5015 16.66 15.1722 16.6602 '
    "15.9996C16.6602 16.8271 15.9897 17.4987 15.1621 17.4987C14.3346 "
    "17.4987 13.6641 16.8271 13.6641 15.9996C13.6642 15.1722 14.3346 "
    '14.5015 15.1621 14.5015Z"></path>'
    "</svg>"
)


_SUN_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" '
    'stroke="currentColor" width="18" height="18" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" '
    'class="shrink-0">'
    '<path stroke-linecap="round" stroke-linejoin="round" '
    'd="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M3 12h2.25m.386-6.364l1.591 1.591"/>'
    '<circle cx="12" cy="12" r="3.75" stroke-linecap="round" '
    'stroke-linejoin="round"/></svg>'
)

_MOON_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" '
    'stroke="currentColor" width="18" height="18" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" '
    'class="shrink-0">'
    '<path stroke-linecap="round" stroke-linejoin="round" '
    'd="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"/></svg>'
)

_SIDEBAR_JS = """\
<script>
function tsInitSidebar() {
  const sidebar = document.getElementById('ts-sidebar');
  const handle = document.getElementById('ts-resize-handle');
  const toggle = document.getElementById('ts-sidebar-toggle');
  if (!sidebar || !handle || !toggle) return false;
  if (sidebar.dataset.tsBound) return true;
  sidebar.dataset.tsBound = '1';
  let collapsed = false;
  let lastWidth = '288px';
  let dragging = false;
  let startX = 0, startW = 0;
  handle.addEventListener('mousedown', function(e) {
    if (collapsed) return;
    dragging = true;
    startX = e.clientX;
    startW = sidebar.offsetWidth;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });
  document.addEventListener('mousemove', function(e) {
    if (!dragging) return;
    let w = Math.max(200, Math.min(500, startW + e.clientX - startX));
    sidebar.style.width = w + 'px';
    lastWidth = w + 'px';
  });
  document.addEventListener('mouseup', function() {
    if (dragging) {
      dragging = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }
  });
  toggle.addEventListener('click', function() {
    collapsed = !collapsed;
    if (collapsed) {
      lastWidth = sidebar.style.width || '288px';
      sidebar.style.width = '0px';
      sidebar.style.overflow = 'hidden';
      handle.style.width = '12px';
    } else {
      sidebar.style.width = lastWidth;
      sidebar.style.overflow = '';
      handle.style.width = '';
    }
  });
  handle.addEventListener('click', function() {
    if (!collapsed) return;
    collapsed = false;
    sidebar.style.width = lastWidth;
    sidebar.style.overflow = '';
    handle.style.width = '';
  });
  return true;
}
function tsTryInit() {
  if (tsInitSidebar()) return;
  const obs = new MutationObserver(function() {
    if (tsInitSidebar()) obs.disconnect();
  });
  obs.observe(document.body, {childList: true, subtree: true});
  setTimeout(function() { obs.disconnect(); }, 10000);
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', tsTryInit);
} else {
  tsTryInit();
}
</script>
"""
_HEADER_JS = """\
<script>
function tsInitHeader() {
  const tsI18n = {
    'ts-i18n-nav-projects': { en: 'Your Projects', zh: '\u4f60\u7684\u9879\u76ee' },
    'ts-i18n-title': { en: 'Your Projects', zh: '\u4f60\u7684\u9879\u76ee' },
    'ts-i18n-import': { en: 'Import', zh: '\u5bfc\u5165' },
   'ts-i18n-new': { en: 'New', zh: '\u65b0\u5efa' },
    'ts-i18n-signin': { en: 'Sign in', zh: '\u767b\u5f55' },
    'ts-i18n-sort-name': { en: 'Name', zh: '\u540d\u79f0' },
    'ts-i18n-sort-date': { en: 'Last edited', zh: '\u6700\u8fd1\u7f16\u8f91' }
  };
  const tsSearchPh = { en: 'Search', zh: '\u641c\u7d22' };
  function tsApplyLang(lang) {
    Object.keys(tsI18n).forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.textContent = tsI18n[id][lang];
    });
    var search = document.querySelector('.ts-search-input');
    if (search) search.setAttribute('placeholder', tsSearchPh[lang]);
  }
  const themeBtn = document.getElementById('ts-theme-toggle');
  const langBtn = document.getElementById('ts-lang-switch');
  if (!themeBtn || !langBtn) return false;
  if (themeBtn.dataset.tsBound) return true;
  themeBtn.dataset.tsBound = '1';
  themeBtn.addEventListener('click', function() {
    const html = document.documentElement;
    const sun = document.getElementById('ts-icon-sun');
    const moon = document.getElementById('ts-icon-moon');
    const isLight = html.getAttribute('data-theme') === 'light';
    if (isLight) {
      html.removeAttribute('data-theme');
      if (sun) sun.style.display = '';
      if (moon) moon.style.display = 'none';
    } else {
      html.setAttribute('data-theme', 'light');
      if (sun) sun.style.display = 'none';
      if (moon) moon.style.display = '';
    }
  });
  langBtn.addEventListener('click', function() {
    const label = langBtn.querySelector('.ts-lang-label');
    if (!label) return;
    const isEn = label.textContent === 'EN';
    label.textContent = isEn ? '\u4e2d' : 'EN';
    tsApplyLang(isEn ? 'zh' : 'en');
  });
  function tsInitSortBtn(btnId, chevId) {
    const btn = document.getElementById(btnId);
    if (!btn || btn.dataset.tsBound) return;
    btn.dataset.tsBound = '1';
    btn.dataset.tsSortDir = 'desc';
    btn.addEventListener('click', function() {
      const chevron = document.getElementById(chevId);
      const dir = btn.dataset.tsSortDir;
      if (dir === 'desc') {
        btn.dataset.tsSortDir = 'asc';
        if (chevron) chevron.style.transform = 'rotate(180deg)';
      } else {
        btn.dataset.tsSortDir = 'desc';
        if (chevron) chevron.style.transform = '';
      }
    });
  }
  tsInitSortBtn('ts-sort-toggle', 'ts-sort-chevron');
  tsInitSortBtn('ts-sort-name-toggle', 'ts-sort-name-chevron');
  return true;
}
function tsTryInitHeader() {
  if (tsInitHeader()) return;
  const obs = new MutationObserver(function() {
    if (tsInitHeader()) obs.disconnect();
  });
  obs.observe(document.body, {childList: true, subtree: true});
  setTimeout(function() { obs.disconnect(); }, 10000);
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', tsTryInitHeader);
} else {
  tsTryInitHeader();
}
</script>
"""


@ui.page("/", title="Thesis Studio")
def home_page() -> None:
    apply_theme()
    ui.add_body_html(_SIDEBAR_JS)
    ui.add_body_html(_HEADER_JS)
    with ui.element("div").classes("flex h-full min-h-0 w-full flex-col"):
        with ui.element("div").classes("min-h-0 flex-1"):
            with ui.element("div").classes("flex h-full w-full flex-col"):
                with ui.element("main").classes("ts-bg-app min-h-0 w-full flex-1"):
                    with ui.element("div").classes(
                        "w-full h-full ts-bg-app box-border "
                        "transition-colors border-2 border-transparent"
                    ):
                        _build_desktop()


def _build_desktop() -> None:
    with ui.element("div").classes("w-full h-full relative"):
        with ui.element("div").classes("flex h-full w-full"):
            _build_sidebar()
            with (
                ui.element("div")
                .classes(
                    "group relative z-20 flex items-center justify-center "
                    "outline-none -mx-1.5 w-3 cursor-col-resize shrink-0 "
                    "transition-colors"
                )
                .props("id=ts-resize-handle")
            ):
                ui.element("div").classes(
                    "rounded-full bg-transparent transition-colors duration-150 h-full w-0.5"
                )
            _build_main_panel()


def _build_sidebar() -> None:
    with (
        ui.element("div")
        .classes("ts-bg-app z-[2000] w-72 shrink-0 transition-[width] duration-200")
        .props("id=ts-sidebar")
    ):
        with ui.element("div").classes("flex flex-col h-full w-full"):
            with ui.element("div").classes(
                "flex flex-row items-center h-16 px-6 pt-4 mb-2 relative"
            ):
                logo()
                ui.element("div").classes("grow")
                _sidebar_toggle()
            with ui.element("div").classes("flex flex-col flex-1 w-full px-6 gap-4"):
                with ui.element("div").classes("flex flex-col pt-3"):
                    with ui.element("div").classes("rounded-lg transition-colors"):
                        _nav_item("Your Projects")
                ui.element("div").classes("grow")
            with ui.element("div").classes("text-sm text-white border-t ts-border-outline"):
                with ui.element("div").classes("flex items-center gap-2 h-12 px-4"):
                    _sign_in_button()
                    ui.element("div").classes("grow")


def _sidebar_toggle() -> None:
    with (
        ui.element("button")
        .classes(
            "ts-btn-tertiary inline-flex items-center justify-center "
            "rounded-full cursor-pointer font-medium h-9 w-9 px-0 gap-0"
        )
        .props("id=ts-sidebar-toggle")
    ):
        ui.html(_SIDEBAR_TOGGLE_ICON)


def _theme_toggle_button() -> None:
    with (
        ui.element("button")
        .classes(
            "ts-btn-tertiary inline-flex items-center justify-center "
            "rounded-full cursor-pointer h-[38px] w-[38px] px-0 gap-0"
        )
        .props("id=ts-theme-toggle")
    ):
        with ui.element("span").props("id=ts-icon-sun"):
            ui.html(_SUN_ICON)
        with ui.element("span").props("id=ts-icon-moon").style("display:none"):
            ui.html(_MOON_ICON)


def _language_switch_button() -> None:
    with (
        ui.element("button")
        .classes(
            "ts-btn-tertiary inline-flex items-center justify-center "
            "rounded-full cursor-pointer h-[38px] px-3 text-sm font-medium"
        )
        .props("id=ts-lang-switch")
    ):
        ui.label("EN").classes("ts-lang-label")


def _build_main_panel() -> None:
    with ui.element("div").classes("p-2 h-full grow min-w-0 relative"):
        with ui.element("div").classes("ts-bg-sidepanel h-full rounded rounded-xl"):
            with ui.element("div").classes("flex flex-col gap-0 h-full"):
                with ui.element("div").classes(
                    "flex flex-row justify-between items-center "
                    "px-5 py-3 gap-3 border-b ts-border-divider"
                ):
                    ui.label("Your Projects").classes(
                        "font-semibold text-lg font-inter ts-text-nav "
                        "flex-1 text-nowrap overflow-hidden text-ellipsis"
                    ).props("id=ts-i18n-title")
                    _theme_toggle_button()
                    _language_switch_button()
                    with ui.element("div").classes("relative shrink-0 w-[300px]"):
                        with ui.element("div").classes(
                            "absolute inset-y-0 start-0 flex "
                            "items-center ps-3.5 pointer-events-none"
                        ):
                            ui.html(_SEARCH_ICON)
                        ui.element("input").props('placeholder="Search"').classes(_SEARCH_INPUT)
                    _button_group()
                with ui.element("div").classes("flex min-h-0 flex-1 flex-col overflow-auto"):
                    with ui.element("div").classes("flex flex-col ts-divide-list"):
                        _build_sort_header()
                        _build_skeleton_items()


def _button_group() -> None:
    with ui.element("div").classes(
        "flex flex-row items-center gap-2 ts-bg-input h-[38px] rounded-full"
    ):
        _list_view_button()
        _grid_view_button()
        _import_button()
        _new_button()


def _list_view_button() -> None:
    with ui.element("button").classes(
        "ts-btn-view-active inline-flex items-center justify-center "
        "rounded-full cursor-pointer p-1.5 h-[38px] w-[38px]"
    ):
        ui.html(_LIST_ICON)


def _grid_view_button() -> None:
    with ui.element("button").classes(
        "ts-btn-view-inactive inline-flex items-center justify-center "
        "rounded-full cursor-pointer p-1.5 h-[38px] w-[38px]"
    ):
        ui.html(_GRID_ICON)


def _import_button() -> None:
    with ui.element("button").classes(
        "ts-btn-secondary inline-flex items-center justify-center gap-2 "
        "rounded-full cursor-pointer font-medium h-[38px] px-4 text-sm"
    ):
        ui.label("Import").props("id=ts-i18n-import")
        ui.html(_CHEVRON_DOWN)


def _new_button() -> None:
    with ui.element("button").classes(
        "ts-btn-primary inline-flex items-center justify-center gap-2 "
        "rounded-full cursor-pointer font-medium h-[38px] px-4 text-sm"
    ):
        ui.html(_PLUS_ICON)
        with ui.element("span").classes("inline-flex items-center gap-2"):
            ui.label("New").props("id=ts-i18n-new")
            ui.html(_CHEVRON_DOWN)


def _build_sort_header() -> None:
    with ui.element("div").classes(
        "flex items-center gap-3 px-5 py-2 text-xs font-medium ts-text-nav-secondary"
    ):
        ui.element("div").classes("w-[50px] flex-none")
        with (
            ui.element("button")
            .classes(
                "inline-flex items-center gap-1 cursor-pointer "
                "ts-text-nav-secondary hover:ts-text-nav transition-colors "
                "flex-1"
            )
            .props("id=ts-sort-name-toggle")
        ):
            ui.label("Name").props("id=ts-i18n-sort-name")
            ui.html(_CHEVRON_DOWN).props("id=ts-sort-name-chevron").classes(
                "transition-transform duration-150"
            )
        with (
            ui.element("button")
            .classes(
                "inline-flex items-center gap-1 cursor-pointer "
                "ts-text-nav-secondary hover:ts-text-nav transition-colors "
                "shrink-0 whitespace-nowrap"
            )
            .props("id=ts-sort-toggle")
        ):
            ui.label("Last edited").props("id=ts-i18n-sort-date")
            ui.html(_CHEVRON_DOWN).props("id=ts-sort-chevron").classes(
                "transition-transform duration-150"
            )
        ui.element("div").classes("w-[26px] flex-none")


def _build_skeleton_items(count: int = 6) -> None:
    for i in range(count):
        delay = -80 * (i + 1)
        with (
            ui.element("div")
            .classes("ts-skeleton-item flex flex-col")
            .style(f"--ts-skeleton-delay: {delay}ms")
        ):
            with ui.element("div").classes("flex items-center gap-3 px-5 py-2 text-sm font-normal"):
                with ui.element("div").classes(
                    "w-[50px] h-[40px] overflow-hidden relative "
                    "flex-none flex items-center justify-center"
                ):
                    ui.element("div").classes("h-[40px] w-[40px] ts-skeleton-bg")
                with ui.element("div").classes(
                    "flex flex-col justify-center flex-1 h-full overflow-hidden w-full"
                ):
                    ui.element("div").classes("h-4 w-48 ts-skeleton-bg")
                with ui.element("div").classes(
                    "ts-text-nav-secondary text-xs font-light text-nowrap py-2 w-20 text-right"
                ):
                    ui.element("div").classes("ml-auto h-3 w-12 ts-skeleton-bg")
                with ui.element("div").classes("ts-text-tertiary flex-none py-2"):
                    ui.element("div").classes("w-[26px] h-[18px] ts-skeleton-bg")


def _nav_item(text: str) -> None:
    cls = (
        "flex w-full items-center gap-2 transition-colors cursor-pointer "
        "py-2.5 pl-4 pr-2 text-sm text-left font-extralight box-border "
        "text-nowrap overflow-hidden text-ellipsis ts-nav-active rounded-lg"
    )
    with ui.element("button").classes(cls):
        label = ui.label(text).classes("flex-1 text-left")
        label.props("id=ts-i18n-nav-projects")


def _sign_in_button() -> None:
    cls = (
        "flex items-center gap-1.5 cursor-pointer rounded-full "
        "py-0.5 pr-1.5 ts-sign-in transition-colors"
    )
    with ui.element("button").classes(cls):
        ui.label("Sign in").classes("text-sm ts-text-nav").props("id=ts-i18n-signin")
        ui.html(_CHEVRON_UP_DOWN)
