"""Export two executive figures from the unchanged published benchmark scores."""
import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
COLORS = {'lev/native': '#08331F', 'openai/gpt-5': '#3B69BC', 'anthropic/claude-opus-5': '#B56750'}
INK = '#17251C'
MUTED = '#59645D'
MODELS = [('lev/native', 'Lev Agent'), ('openai/gpt-5', 'GPT-5 + tools'), ('anthropic/claude-opus-5', 'Opus 5 + tools')]
TASKS = [('extraction', 'Document facts'), ('financial', 'Financial calculations'),
         ('workbook', 'Underwriting workbook'), ('memo', 'Financing memo'), ('evidence', 'Source citations')]


def aggregate_workflow(data):
    out = []
    for system, label in MODELS:
        runs = [r for r in data['runs'] if r['system'] == system and r['track'] != 'direct']
        assert len(runs) == 6 and all(r['status'] == 'completed' for r in runs)
        row = dict(system=system, label=label, cost=sum(r['cost_usd'] if r['cost_usd'] is not None else r['known_partial_cost_usd'] for r in runs))
        for task, _ in TASKS:
            if task in ('extraction', 'financial'):
                scores = [r['field_scores'][task] for r in runs]
            elif task == 'evidence':
                scores = [r['evidence_score'] for r in runs]
            else:
                checks = [c for r in runs for c in (r['workbook_audit']['checks'] + r['review']['workbook'] if task == 'workbook' else r['review']['memo'])]
                scores = [dict(passed=sum(c['passed'] for c in checks), total=len(checks))]
            row[task] = dict(passed=sum(s['passed'] for s in scores), total=sum(s['total'] for s in scores))
        out.append(row)
    return out


def header(fig, title, subtitle):
    fig.text(.045, .956, 'CRE BENCH', color=COLORS['lev/native'], fontsize=12, weight='bold', va='center')
    fig.text(.955, .956, 'Published by Lev  /  September 2026', ha='right', color=MUTED, fontsize=10, va='center')
    fig.text(.045, .891, title, color=INK, fontsize=29, weight='bold')
    fig.text(.045, .848, subtitle, color=MUTED, fontsize=12.5)


def axis_style(ax, maximum, ticks, percent=False):
    ax.set_xlim(0, maximum)
    ax.set_xticks(ticks)
    if percent:
        ax.xaxis.set_major_formatter(PercentFormatter())
    ax.set_axisbelow(True)
    ax.grid(axis='x', color='#E1E6E3', linewidth=.7)
    for name in ('top', 'right', 'left'):
        ax.spines[name].set_visible(False)
    ax.spines['bottom'].set_color('#BAC6BE')
    ax.tick_params(axis='both', length=0, labelcolor=MUTED, labelsize=10)


def financing(rows):
    fig = plt.figure(figsize=(16, 10))
    header(fig, 'Financing workflow quality', 'Rubric checks passed across six synthetic cases · Native Lev and two tool-assisted model baselines')
    for i, row in enumerate(rows):
        x = .24 + i * .25
        fig.patches.append(Rectangle((x, .79), .012, .012, transform=fig.transFigure, color=COLORS[row['system']]))
        fig.text(x+.019, .79, row['label'], fontsize=12.5, weight='bold', color=INK)
        fig.text(x+.019, .766, f"Six-case inference: ${row['cost']:.2f}" + (' estimated' if i == 0 else ' reported'), fontsize=10, color=MUTED)
    ax = fig.add_axes([.24, .24, .55, .46])
    axis_style(ax, 100, [0, 25, 50, 75, 100], True)
    centers = [i * 1.55 for i in range(len(TASKS))]
    for group, (task, label) in enumerate(TASKS):
        for j, row in enumerate(rows):
            score = row[task]
            value = 100 * score['passed'] / score['total']
            y = centers[group] + (j-1)*.30
            ax.barh(y, value, height=.23, color=COLORS[row['system']], edgecolor=COLORS[row['system']], linewidth=.6)
            ax.text(102, y, f'{value:.1f}%', va='center', fontsize=12, color=INK)
            ax.text(114, y, f"{score['passed']}/{score['total']}", va='center', fontsize=11, color=MUTED, fontfamily='DejaVu Sans Mono')
    ax.set_yticks(centers, [label for _, label in TASKS], fontsize=13, color=INK)
    ax.tick_params(axis='y', pad=17)
    ax.set_ylim(centers[-1]+.6, -.6)
    fig.text(.045, .16, 'Lev ties on facts and calculations. Opus 5 leads workbook, memo and citation checks.', fontsize=14, color=INK)
    fig.text(.045, .115, 'Direct-call financial comparison on five mutually readable packets: Lev 110/110; GPT-5 89/110; Opus 5 110/110.', fontsize=11, color=MUTED)
    fig.text(.045, .078, 'One attempt per case; author-reviewed diagnostics, not independent validation. Lev: Agent 7.9 / Opus 4.7. Tools and compute differ.', fontsize=10, color=MUTED)
    fig.text(.045, .052, 'Costs cover inference only; subscriptions, operator time and platform overhead are excluded. Direct API controls are not plotted above.', fontsize=10, color=MUTED)
    fig.text(.045, .026, 'Source: crebench.vercel.app/financing · Original counts, outputs and rubric are public.', fontsize=10, color=MUTED)
    return fig


def research(data):
    rows = data['summary']
    assert len(rows) == 5 and all(r['target'] == 99 for r in rows)
    fig = plt.figure(figsize=(16, 9.5))
    header(fig, 'Comp and lead research performance', '24 synthetic cases per condition · Sales comps, rent comps, sponsors and refinance leads · Scoring v1.1')
    specifications = [(.255, .19, 'Verified shortlist yield', 'Correct facts + sources; higher is better', 100, [0, 50, 100]),
                      (.545, .16, 'Ineligible entries', 'Incorrect inclusions; lower is better', 8, [0, 2, 4, 6, 8]),
                      (.785, .14, 'Inference cost', 'USD across 24 planned cases', 16, [0, 5, 10, 15])]
    axes = []
    for left, width, title, sub, maximum, ticks in specifications:
        fig.text(left, .755, title, fontsize=15, color=INK, weight='bold')
        fig.text(left, .723, sub, fontsize=9.5, color=MUTED)
        ax = fig.add_axes([left, .245, width, .405])
        axis_style(ax, maximum, ticks, maximum == 100)
        ax.set_ylim(4.6, -.6)
        ax.set_yticks([])
        axes.append(ax)
    for i, row in enumerate(rows):
        color = COLORS[row['system']]
        direct = row['track'] == 'direct'
        fill = 'white' if direct else color
        hatch = '////' if direct else None
        y = .245 + .405 * (4.6-i)/5.2
        fig.text(.045, y+.006, row['label'], fontsize=12.5, weight='bold', color=INK, va='center')
        sc = row['screening']
        screening_percent = (Decimal(sc['passed']) * 100 / Decimal(sc['total'])).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
        fig.text(.045, y-.02, f"Screening: {sc['passed']}/{sc['total']} ({screening_percent}%)", fontsize=9.5, color=MUTED, va='center')
        values = [100*row['verified']/row['target'], row['returned']-row['eligible'], row['cost_total_usd']]
        for ax, value in zip(axes, values):
            ax.barh(i, value, height=.48, color=fill, edgecolor=color, hatch=hatch, linewidth=.9)
        axes[0].text(103, i, f"{values[0]:.1f}%\n{row['verified']}/{row['target']}", va='center', fontsize=11.5, color=INK)
        axes[1].text(values[1]+.24, i, str(values[1]), va='center', fontsize=12, color=INK)
        cost = ('≥ ' if row['costs_recorded']<row['planned'] else '') + f"${values[2]:.2f}" + ('*' if i==0 else '')
        axes[2].text(values[2]+.5, i, cost, va='center', fontsize=11.5, color=INK)
    fig.text(.045, .16, 'Lev matches the leading verified yield, but seven ineligible selections reduce its precision to 93.4%.', fontsize=13.5, color=INK)
    fig.text(.045, .113, 'GPT-5 direct completed 23/24 cases. Its timeout leaves three slots and 20 decisions unanswered; two request charges are unknown.', fontsize=10, color=MUTED)
    fig.text(.045, .086, '*Lev cost is a model-rate estimate; API costs are reported inference. Direct controls create no files. Subscription and operator costs excluded.', fontsize=10, color=MUTED)
    fig.text(.045, .059, 'Supplied fictional extracts, not live discovery. Author-reviewed; four shared templates. Native internal access is partly observable, not verified equal.', fontsize=10, color=MUTED)
    fig.text(.045, .032, 'Source: crebench.vercel.app/research · All four no-match cases were handled correctly by every condition.', fontsize=10, color=MUTED)
    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    sources = ['experiments/2026-09-06-workflow-v1/results.json', 'experiments/2026-09-07-research-v1/results.json']
    workflow, research_data = [json.loads((ROOT/p).read_text()) for p in sources]
    finance_rows = aggregate_workflow(workflow)
    plt.rcParams.update({'font.family':'DejaVu Sans', 'text.parse_math':False, 'svg.fonttype':'path', 'font.size':11})
    figures = [('financing-summary', financing(finance_rows)), ('research-summary', research(research_data))]
    with PdfPages(out/'benchmark-summary.pdf') as pdf:
        for name, fig in figures:
            for extension in ['png', 'svg']:
                fig.savefig(out/f'{name}.{extension}', dpi=180, facecolor='white')
            pdf.savefig(fig, facecolor='white')
            plt.close(fig)
    with (out/'chart-data.csv').open('w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['cohort','condition','measure','numerator_or_usd','denominator','cost_basis'])
        for row in finance_rows:
            for key, label in TASKS:
                writer.writerow(['financing',row['label'],label,row[key]['passed'],row[key]['total'],''])
            writer.writerow(['financing',row['label'],'inference_usd',row['cost'],'','estimated' if row['system']=='lev/native' else 'reported'])
        for row in research_data['summary']:
            for key, n, d in [('verified',row['verified'],row['target']), ('ineligible',row['returned']-row['eligible'],row['returned']),
                              ('screening',row['screening']['passed'],row['screening']['total'])]:
                writer.writerow(['research',row['label'],key,n,d,''])
            writer.writerow(['research',row['label'],'inference_usd',row['cost_total_usd'],'',
                             'estimated' if row['track']=='lev_native' else 'reported_lower_bound' if row['costs_recorded']<24 else 'reported'])
    (out/'source-manifest.json').write_text(json.dumps({'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
        'renderer':'Matplotlib', 'research_scoring_version':research_data['version'], 'original_scores_modified':False},indent=2)+'\n')
    print(out)


if __name__ == '__main__':
    main()
