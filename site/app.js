const tabs = [...document.querySelectorAll('[role="tab"]')];
for (const tab of tabs) {
  const activate = () => {
    for (const other of tabs) {
      const selected = other === tab;
      other.setAttribute('aria-selected', String(selected));
      other.tabIndex = selected ? 0 : -1;
      document.getElementById(other.getAttribute('aria-controls')).hidden = !selected;
    }
  };
  tab.addEventListener('click', activate);
  tab.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const i = tabs.indexOf(tab);
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 :
      (i + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].click(); tabs[next].focus();
  });
}
for (const button of document.querySelectorAll('[data-filter]')) {
  button.addEventListener('click', () => {
    for (const b of document.querySelectorAll('[data-filter]')) b.setAttribute('aria-pressed', String(b === button));
    let count = 0;
    for (const task of document.querySelectorAll('[data-layer]')) {
      task.hidden = button.dataset.filter !== 'all' && task.dataset.layer !== button.dataset.filter;
      if (!task.hidden) count++;
    }
    document.getElementById('task-count').textContent = `${count} task families shown`;
  });
}
const rate = document.getElementById('interest-rate');
if (rate) {
  rate.addEventListener('input', () => {
    const annual = Number(rate.value) / 100;
    const dscr = 150000 / (1.25 * annual);
    const constraints = {LTV: 1560000, DSCR: dscr, 'Debt yield': 150000 / .09};
    const binding = Object.keys(constraints).reduce((a,b) => constraints[a] < constraints[b] ? a : b);
    const money = value => new Intl.NumberFormat('en-US', {style:'currency',currency:'USD',maximumFractionDigits:0}).format(value);
    document.getElementById('rate-label').textContent = `${Number(rate.value).toFixed(2)}%`;
    document.getElementById('dscr-limit').textContent = money(dscr);
    document.getElementById('loan-limit').textContent = money(constraints[binding]);
    document.getElementById('binding').textContent = `${binding} is the binding constraint.`;
  });
}
