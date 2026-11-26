/**
 * Client side of the projects directory. The page is fully rendered at build
 * time; this script only reads the URL, applies src/lib/filter.ts, toggles the
 * cards' `hidden` attribute, reorders them and writes the state back to the
 * URL with `history.replaceState`.
 */
import {
  DEFAULT_STATE,
  activeFilters,
  applyFilters,
  categoryOptions,
  parseState,
  serialiseState,
  versionOptions,
  withProtocol,
  withoutFilter,
  type FilterKey,
  type FilterProject,
  type FilterState,
  type Option,
  type SortKey,
} from '../lib/filter';
import type { Curation } from '../lib/data';

function byId<T extends HTMLElement>(id: string): T {
  const element = document.getElementById(id);
  if (!element) throw new Error(`projects directory: #${id} is missing`);
  return element as T;
}

function fillSelect(select: HTMLSelectElement, anyLabel: string, options: Option[], value: string | null): void {
  const wanted = value ?? '';
  const choices = [{ value: '', label: anyLabel }, ...options];
  // A value from the URL that the data does not offer stays selectable, so
  // the control shows what is actually applied.
  if (wanted && !options.some((o) => o.value === wanted)) choices.push({ value: wanted, label: wanted });
  select.replaceChildren(...choices.map((o) => new Option(o.label, o.value)));
  select.value = wanted;
}

const SVG = 'http://www.w3.org/2000/svg';

function closeIcon(): SVGSVGElement {
  const svg = document.createElementNS(SVG, 'svg');
  for (const [k, v] of Object.entries({
    'aria-hidden': 'true',
    width: '14',
    height: '14',
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    'stroke-width': '2.5',
    'stroke-linecap': 'round',
  })) {
    svg.setAttribute(k, v);
  }
  const path = document.createElementNS(SVG, 'path');
  path.setAttribute('d', 'M6 6l12 12M18 6L6 18');
  svg.append(path);
  return svg;
}

export function initProjectsDirectory(): void {
  const projects = JSON.parse(byId('projects-data').textContent ?? '[]') as FilterProject[];
  const form = byId<HTMLFormElement>('filters');
  const q = byId<HTMLInputElement>('f-q');
  const protocol = byId<HTMLSelectElement>('f-protocol');
  const category = byId<HTMLSelectElement>('f-category');
  const version = byId<HTMLSelectElement>('f-version');
  const language = byId<HTMLSelectElement>('f-language');
  const host = byId<HTMLSelectElement>('f-host');
  const sort = byId<HTMLSelectElement>('f-sort');
  const states = [...form.querySelectorAll<HTMLInputElement>('input[name="state"]')];
  const toggle = byId<HTMLButtonElement>('filters-toggle');
  const toggleLabel = byId('filters-toggle-label');
  const panel = byId('filter-panel');
  const chips = byId<HTMLUListElement>('active-filters');
  const count = byId('results-count');
  const empty = byId('results-empty');
  const list = byId<HTMLUListElement>('results');
  const cards = new Map(
    [...list.querySelectorAll<HTMLLIElement>('li[data-id]')].map((li) => [li.dataset.id as string, li]),
  );
  // The build rendered the options that do not depend on the state; keep them.
  const fixed = (select: HTMLSelectElement) => ({
    any: select.options[0]?.text ?? '',
    options: [...select.options].slice(1).map((o) => ({ value: o.value, label: o.text })),
  });
  const protocolOpts = fixed(protocol);
  const languageOpts = fixed(language);
  const hostOpts = fixed(host);

  let state: FilterState = parseState(window.location.search);

  function render(): void {
    q.value = state.q;
    fillSelect(protocol, protocolOpts.any, protocolOpts.options, state.protocol);
    fillSelect(category, 'All categories', categoryOptions(projects, state.protocol), state.category);
    // A category belongs to a protocol: pick the protocol first.
    category.disabled = state.protocol === null && state.category === null;
    fillSelect(version, 'Any version', versionOptions(projects, state.protocol), state.version);
    fillSelect(language, languageOpts.any, languageOpts.options, state.language);
    fillSelect(host, hostOpts.any, hostOpts.options, state.host);
    for (const box of states) box.checked = state.states.includes(box.value as Curation);
    sort.value = state.sort;

    const shown = applyFilters(projects, state);
    const shownIds = new Set(shown.map((p) => p.id));
    const order = [...shown, ...projects.filter((p) => !shownIds.has(p.id))];
    for (const p of order) {
      const card = cards.get(p.id);
      if (!card) continue;
      card.hidden = !shownIds.has(p.id);
      list.append(card);
    }
    const total = projects.length;
    count.textContent = `${shown.length} of ${total} ${total === 1 ? 'project' : 'projects'}`;
    empty.hidden = shown.length > 0;

    const active = activeFilters(state);
    chips.replaceChildren(
      ...active.map((chip) => {
        const li = document.createElement('li');
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.filter = chip.key;
        button.setAttribute('aria-label', `Remove filter: ${chip.label}`);
        button.append(chip.label, closeIcon());
        li.append(button);
        return li;
      }),
    );
    chips.hidden = active.length === 0;
    const panelFilters = active.filter((chip) => chip.key !== 'q').length;
    toggleLabel.textContent = panelFilters ? `Filters · ${panelFilters}` : 'Filters';

    const query = serialiseState(state);
    const target = `${window.location.pathname}${query ? `?${query}` : ''}${window.location.hash}`;
    if (target !== `${window.location.pathname}${window.location.search}${window.location.hash}`) {
      history.replaceState(history.state, '', target);
    }
  }

  function update(next: FilterState): void {
    state = next;
    render();
  }

  function readForm(changed: EventTarget | null): FilterState {
    const value = (select: HTMLSelectElement) => select.value || null;
    if (changed === protocol) return withProtocol(state, value(protocol));
    return {
      q: q.value,
      protocol: state.protocol,
      category: value(category),
      version: value(version),
      language: value(language),
      host: value(host),
      states: states.filter((box) => box.checked).map((box) => box.value as Curation),
      sort: sort.value as SortKey,
    };
  }

  form.addEventListener('submit', (event) => event.preventDefault());
  form.addEventListener('input', (event) => {
    // Typing in the search box keeps the caret: only the results re-render.
    if (event.target === q) {
      state = { ...state, q: q.value };
      const caret = q.selectionStart;
      render();
      q.setSelectionRange(caret, caret);
    }
  });
  form.addEventListener('change', (event) => {
    if (event.target !== q) update(readForm(event.target));
  });
  sort.addEventListener('change', () => update({ ...state, sort: sort.value as SortKey }));
  byId('filters-reset').addEventListener('click', () => update({ ...DEFAULT_STATE, states: [...DEFAULT_STATE.states] }));
  chips.addEventListener('click', (event) => {
    const button = (event.target as Element).closest<HTMLButtonElement>('button[data-filter]');
    if (!button) return;
    update(withoutFilter(state, button.dataset.filter as FilterKey));
    (chips.querySelector('button') ?? q).focus();
  });
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    panel.classList.toggle('is-open', open);
  });

  form.hidden = false;
  byId('sort-wrap').hidden = false;
  render();
}
