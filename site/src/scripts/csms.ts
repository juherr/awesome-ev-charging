/**
 * Client side of the CSMS directory. The table is fully rendered at build
 * time; this script reads the URL, applies src/lib/csms.ts to each row's data
 * attributes, toggles their `hidden` attribute and writes the state back with
 * `history.replaceState`. The product details below the table stay listed.
 */
import { DEFAULT_CSMS_STATE, matchesCsms, parseCsmsState, serialiseCsmsState, type CsmsFilterRow, type CsmsFilterState } from '../lib/csms';

function byId<T extends HTMLElement>(id: string): T {
  const element = document.getElementById(id);
  if (!element) throw new Error(`CSMS directory: #${id} is missing`);
  return element as T;
}

export function initCsmsDirectory(): void {
  const form = byId<HTMLFormElement>('csms-filters');
  const q = byId<HTMLInputElement>('c-q');
  const certified = byId<HTMLInputElement>('c-certified');
  const source = byId<HTMLInputElement>('c-source');
  const count = byId<HTMLElement>('csms-count');
  const empty = byId<HTMLElement>('csms-empty');
  const rows = [...document.querySelectorAll<HTMLTableRowElement>('#csms-table tbody tr')].map((tr) => ({
    tr,
    data: {
      text: tr.dataset.text ?? '',
      certified: tr.dataset.certified === '1',
      source: tr.dataset.source === '1',
    } satisfies CsmsFilterRow,
  }));
  const total = rows.length;

  function render(state: CsmsFilterState): void {
    let shown = 0;
    for (const { tr, data } of rows) {
      const match = matchesCsms(data, state);
      tr.hidden = !match;
      if (match) shown++;
    }
    count.textContent = `${shown} of ${total} products`;
    empty.hidden = shown > 0;
  }

  function readForm(): CsmsFilterState {
    return { q: q.value, certified: certified.checked, source: source.checked };
  }

  function apply(): void {
    const state = readForm();
    render(state);
    const query = serialiseCsmsState(state);
    history.replaceState(history.state, '', `${location.pathname}${query ? `?${query}` : ''}${location.hash}`);
  }

  const initial = parseCsmsState(location.search);
  q.value = initial.q;
  certified.checked = initial.certified;
  source.checked = initial.source;

  form.addEventListener('input', apply);
  form.addEventListener('change', apply);
  form.addEventListener('submit', (event) => event.preventDefault());
  byId<HTMLButtonElement>('csms-reset').addEventListener('click', () => {
    q.value = DEFAULT_CSMS_STATE.q;
    certified.checked = DEFAULT_CSMS_STATE.certified;
    source.checked = DEFAULT_CSMS_STATE.source;
    apply();
  });

  form.hidden = false;
  render(initial);
}
