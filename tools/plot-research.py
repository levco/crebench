"""Export the publication figures directly from the recorded research matrix."""
import argparse
import json
import textwrap
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/2026-09-07-research-v1'
COLORS = {'lev/native': '#08331F', 'openai/gpt-5': '#3B69BC', 'anthropic/claude-opus-5': '#B56750'}
TASKS = [('sales_comps', 'Sales comps'), ('rent_comps', 'Rent comps'), ('sponsor_leads', 'Sponsor leads'), ('refinance_leads', 'Refinance leads')]

def export(fig, directory, name):
    for extension in ['svg', 'png']:
        fig.savefig(directory / (name + '.' + extension), dpi=190, facecolor='white')
    plt.close(fig)

def footer(fig, text):
    fig.text(.035, .027, text, size=9, color='#536057', va='bottom')

def setup(ax):
    ax.set_axisbelow(True)
    ax.grid(axis='x', color='#E1E7E3', linewidth=.7)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#CBD4CE')
    ax.tick_params(axis='both', length=0, labelcolor='#303C34')

def quality(data, directory, direct=False, screening=False, mobile=False):
    fig, axes = plt.subplots(4 if mobile else 2, 1 if mobile else 2, figsize=(7,18) if mobile else (13.5,8.2))
    if mobile:
        fig.subplots_adjust(left=.32,right=.79,top=.84,bottom=.10,hspace=.75)
    else:
        fig.subplots_adjust(left=.15, right=.88, top=.82, bottom=.15, hspace=.64, wspace=.75)
    name = 'research-screening' if screening else 'research-direct-quality' if direct else 'research-agent-quality'
    heading = 'Candidate screening success' if screening else 'Verified shortlist yield — direct API comparison' if direct else 'Verified shortlist yield — native and general agents'
    fig.text(.035, .96 if mobile else .95, textwrap.fill(heading,38) if mobile else heading, fontsize=19 if mobile else 20, weight='bold', color='#16251C',va='top' if mobile else 'baseline')
    subtitle = 'Six cases and 120 candidate decisions per task / system. Includes unanswered decisions after a transport failure.' if screening else 'Six cases per task / system. Correct facts and supporting sources required; unanswered slots get no credit; empty cases assessed separately.'
    fig.text(.035, .89 if mobile else .895, textwrap.fill(subtitle,65) if mobile else subtitle, fontsize=10.5, color='#536057')
    for ax, (task, label) in zip(axes.flat, TASKS):
        rows = [r for r in data['tasks'] if r['task'] == task and (screening or r['track'] == 'lev_native' or r['track'] == ('direct' if direct else 'agent'))]
        setup(ax)
        for i, row in enumerate(rows):
            numerator, denominator = (row['screening']['passed'], row['screening']['total']) if screening else (row['verified'], row['target'])
            if not denominator:
                ax.text(4, i, 'Not scored', va='center', fontsize=9, color='#536057')
                continue
            val = 100 * numerator / denominator if denominator else 0
            color = COLORS[row['system']]
            ax.barh(i, val, height=.57, color='white' if row['track'] == 'direct' else color,
                    edgecolor=color, hatch='////' if row['track'] == 'direct' else None, linewidth=1)
            ax.text(104, i, f'{val:.1f}%\n{numerator}/{denominator}' if mobile else f'{val:.1f}%  {numerator}/{denominator}', va='center', fontsize=13 if mobile else 9, color='#16251C', clip_on=False)
        ax.set_yticks(range(len(rows)), [r['label'] for r in rows], fontsize=13 if mobile else 9)
        ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xticks([0, 50, 100]); ax.xaxis.set_major_formatter(PercentFormatter())
        ax.set_title(label, loc='left', pad=16, fontsize=14, weight='bold')
    note='CRE Bench by Lev · Original synthetic cases; one attempt per condition · Scoring v1.1; one GPT-5 direct run timed out (no credit).\nSupplied extracts, not live discovery or ingestion. Native internal execution is partly observable; equal data access is unverified.'
    footer(fig, textwrap.fill(note.replace('\n',' '),77) if mobile else note)
    export(fig, directory, name+('-mobile' if mobile else ''))

def cost(data, directory):
    fig, ax = plt.subplots(figsize=(11.5, 5.8));fig.subplots_adjust(left=.19, right=.77, top=.76, bottom=.20)
    setup(ax)
    rows = data['summary']
    for i, row in enumerate(rows):
        value = row['cost_total_usd'];color = COLORS[row['system']]
        ax.barh(i, value, height=.56, color='white' if row['track'] == 'direct' else color, edgecolor=color, hatch='////' if row['track'] == 'direct' else None)
        incomplete = row['costs_recorded'] < row['planned']
        basis = 'lower bound; 1 run unpriced' if incomplete else 'estimated' if row['track'] == 'lev_native' else 'reported'
        ax.text(value + .15, i, (f'≥ ${value:.2f}  ·  {basis}' if incomplete else f'${value:.2f}  ·  ${value / 24:.2f} / case  ·  {basis}'), va='center', fontsize=10, clip_on=False)
    ax.set_yticks(range(5), [r['label'] for r in rows]);ax.invert_yaxis();ax.set_xlim(0, max(r['cost_total_usd'] for r in rows) * 1.15)
    ax.set_xlabel('Recorded inference cost for the 24-case condition, USD', labelpad=12)
    fig.text(.035, .93, 'Research inference cost', fontsize=22, weight='bold', color='#16251C')
    fig.text(.035, .865, 'Recorded charges shown. Two timed-out GPT-5 direct requests have unknown charges.', fontsize=11, color='#536057')
    footer(fig, 'CRE Bench by Lev · API: gateway-reported charge. Lev: matched trace model-rate estimate.\nExcludes subscription prices, operator time, session naming, hosting and non-inference overhead. Product credits are not dollars.')
    export(fig, directory, 'research-cost')

def matrix(data, directory):
    labels = [r['label'] for r in data['summary']]
    cases = [c for prefix, _ in TASKS for c in data['case_ids'] if c.startswith(prefix.replace('_', '-'))]
    values = np.full((24, 5), np.nan)
    for i, case in enumerate(cases):
        for j, label in enumerate(labels):
            row = next(r for r in data['runs'] if r['case_id'] == case and r['label'] == label)
            if row.get('grade'):
                score = row['grade']['candidate_accuracy'];values[i, j] = 100 * score['passed'] / score['total']
    fig, ax = plt.subplots(figsize=(10, 12.5));fig.subplots_adjust(left=.32, right=.84, top=.88, bottom=.10)
    cmap = LinearSegmentedColormap.from_list('screening', ['#FFFFFF', '#C3D9CA', '#08331F'])
    im = ax.imshow(values, vmin=0, vmax=100, cmap=cmap, aspect='auto')
    ax.set_yticks(range(24), cases, fontsize=9);ax.set_xticks(range(5), labels, rotation=28, ha='right', fontsize=9);ax.tick_params(length=0)
    for i in range(24):
        for j in range(5):
            val = values[i, j]
            ax.text(j, i, f'{val:.0f}%' if np.isfinite(val) else 'Timeout', ha='center', va='center', fontsize=10, color='white' if val > 60 else '#16251C')
    for i in [5.5, 11.5, 17.5]:ax.axhline(i, color='white', linewidth=3)
    for spine in ax.spines.values():spine.set_visible(False)
    fig.colorbar(im, ax=ax, fraction=.033, pad=.045, label='Correct candidate decisions, %', ticks=[0, 50, 100])
    fig.text(.035, .953, 'Screening by case; timeout shown separately', fontsize=22, weight='bold', color='#16251C')
    fig.text(.035, .922, 'Each cell: 20 accept/reject decisions. Six correlated variants per task family.', fontsize=10, color='#536057')
    footer(fig, 'CRE Bench by Lev · Shared fictional source corpus · Four zero-match cases are included.\nNative internal execution has partial audit coverage; equal data access is unverified. This measures screening only.')
    export(fig, directory, 'research-case-matrix')

def errors(data, directory):
    fig, ax = plt.subplots(figsize=(11.5, 5.8));fig.subplots_adjust(left=.19, right=.84, top=.76, bottom=.20)
    setup(ax)
    for i, row in enumerate(data['summary']):
        value = row['cases_with_material_errors'];color = COLORS[row['system']]
        ax.barh(i, value, height=.56, color='white' if row['track'] == 'direct' else color, edgecolor=color,
                hatch='////' if row['track'] == 'direct' else None)
        ax.text(value + .35, i, f'{value} / {row["graded"]} cases · {row["material_errors"]} findings', va='center', fontsize=10)
    ax.set_yticks(range(5), [r['label'] for r in data['summary']]);ax.invert_yaxis();ax.set_xlim(0, 24);ax.set_xticks([0, 6, 12, 18, 24])
    ax.set_xlabel('Cases with at least one consequential shortlist error (lower is better)', labelpad=12)
    fig.text(.035, .93, 'Cases with material shortlist errors', fontsize=22, weight='bold', color='#16251C')
    fig.text(.035, .865, 'Ineligible or duplicate selections, invented records, and materially incorrect selected facts.', fontsize=10.5, color='#536057')
    footer(fig, 'CRE Bench by Lev · 24 attempted cases per condition; GPT-5 direct returned 23 answers. Transport failure is not a factual finding.\nScreening decisions, missing fields, source-ID compliance and artifact formatting are assessed separately.')
    export(fig, directory, 'research-material-errors')

if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--preview', action='store_true');args = parser.parse_args()
    data = json.loads((EXP / 'results.json').read_text())
    if not args.preview and any(r['status'] in ('running', 'not_started') for r in data['runs']):
        raise ValueError('Final publication figures require every planned run to finish')
    directory = ROOT / 'work/research-v1/figure-preview' if args.preview else EXP / 'figures'
    directory.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'path', 'font.size': 10, 'text.parse_math': False})
    quality(data, directory);quality(data, directory, direct=True);quality(data, directory, screening=True);cost(data, directory);matrix(data, directory);errors(data, directory)
    quality(data,directory,mobile=True);quality(data,directory,direct=True,mobile=True);quality(data,directory,screening=True,mobile=True)
    print(directory)
