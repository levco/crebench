# Website design

CRE Bench is a research publication from Lev. The interface puts the evaluation evidence before promotional claims.

## Visual system

- White editorial pages, Lev forest green (`#08331F`), and locally hosted IBM Plex Sans and IBM Plex Mono.
- Official, unmodified Lev publisher marks in the masthead and footer. Font licenses and trademark attribution live in `site/assets/`.
- A homepage execution matrix generated directly from the retained pilot's `financial-v2.json`. Each row includes all 30 financial checks, its pass count, an accessible failure summary, and a link to the full report. Color is supplemented with failure marks.
- Source tables and worked answers share a two-column inspection view. On small screens, they stack; wide result tables and code samples scroll within their own regions.
- Shared navigation, keyboard focus, keyboard-operated example tabs, task filters, and reduced-motion support.

The pilot label and one-case limitation stay next to the matrix. This design introduces no new benchmark results or ranking claims.

## References

Reviewed on September 6, 2026:

- [OpenAI Evals](https://evals.openai.com/): direct access to research, datasets, and evaluation resources.
- [Scale Labs](https://labs.scale.com/): restrained technical typography and clear research navigation.
- [Harvey's Legal Agent Benchmark](https://www.harvey.ai/blog/introducing-harveys-legal-agent-benchmark): visible company ownership and domain-specific scope.

These are design references, not endorsements or affiliations. No reference site's brand assets, artwork, or source code are included.

## Validation

Run `npm run build` and `npm run check:site`. Browser review covers the desktop home/results/example/task views, narrow layouts at 320, 390, and 500 pixels, keyboard tabs, task filtering, and the interest-rate sensitivity. The 10% scenario must bind at DSCR with a $1,200,000 loan limit.
