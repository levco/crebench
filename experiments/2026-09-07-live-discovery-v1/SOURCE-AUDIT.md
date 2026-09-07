# Source audit: initial findings

Audit performed September 7, 2026 by the benchmark authoring assistant. This is
an initial source inspection, not independent practitioner qualification or a
complete accuracy score. Original model answers remain unchanged. Sources below
were opened; findings describe their text, not search snippets. Publication dates
are not automatically closing dates. Unchecked fields and briefs remain pending.

## Atlanta apartment sales

Lev returned three transactions supported by the cited reporting: Block Lofts
(244 rental units, excluding 69 condos), Cortland at Armour Yards (372 units),
and Millworks (345 units). The articles explicitly give the respective closing
dates of March 11, April 10, and August 28, 2025. Prices of $69.5 million and
$78 million are supported for Block Lofts and Millworks. Sources:
[Block Lofts](https://www.bisnow.com/news/atlanta/multifamily/old-fourth-ward-apartments-doubles-price-in-sale-to-ares-128724),
[Armour Yards](https://www.bisnow.com/news/atlanta/deal-sheet/this-weeks-atlanta-deal-sheet-cortland-buys-armour-yards-apartments-129103),
[Millworks](https://www.bisnow.com/news/atlanta/multifamily/nuveen-picks-up-west-midtown-apartment-complex-for-more-than-70m-130891).

Lev correctly describes Armour Yards' disclosed price as exceeding $71 million
in its explanation, but places 71000000 in the numeric price field. The numeric
schema needs a bound qualifier; downstream users must not treat that field as
an exact price. This limitation is visible in the unaltered answer.

GPT-5 returned 1105 Town Brookhaven, the Lofts at Twenty25, and Perimeter Gardens.
The opened [Brookhaven report](https://www.connectcre.com/stories/mesirow-pays-87m-for-town-brookhaven-apartments/)
supports 299 units, $87 million and Mesirow as buyer. The opened
[Perimeter Gardens report](https://www.connectcre.com/stories/new-york-life-acquires-245-unit-dunwoody-apartment-project/)
supports 245 units, $53.5 million and New York Life as buyer, but November 18 is
the article date; the exact closing date returned by GPT-5 is not established
there. The Lofts' December 23 closing day also needs additional support: an
acquisition news listing is not proof of that day. Remaining address, source-date
and transaction checks are pending. Opus 5 reached its original turn limit
without submitting a final Atlanta answer; no candidate accuracy is assigned.

## Dallas industrial sales

Both Lev and GPT-5 found 2800 Skyline. The
[JLL release](https://www.jll.com/en-us/newsroom/wp-carey-acquires-2800-skyline-in-east-dallas-submarket)
supports W. P. Carey, 756,668 SF, Mesquite and a September 2025 completion,
separate from its November 3 publication. Lev retained the closing month;
GPT-5 left the transaction date null and missed this available detail.

Lev's I-20 Dallas Crossing result is supported by the
[buyer announcement](https://www.sealynet.com/news/sealy-company-adds-413480-square-foot-modern-distribution-asset-in-south-dallas/)
for 413,480 SF, Dallas, Sealy and a completed purchase. September 25 is the
release dateline; September 29 is the website date. The exact closing day that
Lev supplies is not expressly established by the dateline alone.

Lev's Red River result is supported by the
[Bixby announcement](https://www.businesswire.com/news/home/20250521410911/en/Bixby-Capital-Management-Acquires-Red-River-Business-Park-in-High-Growth-DFW-Industrial-Corridor)
for Lewisville, three buildings, 241,104 SF and Bixby as buyer. However, the row
pairs an acquisitions executive's name with the marketing contact's email.
Its explanation discloses this difference, but the structured name/email pair
is unsuitable for direct CRM use. No outreach occurred.

GPT-5's Elizabeth Creek result matches the
[JLL release](https://www.jll.com/en-us/newsroom/1m-sf-of-class-a-industrial-product-trades-hands-in-dfw)
on buyer, location, two buildings and 1,106,064 SF. The March 14 announcement
does not provide an exact closing day; GPT-5 leaves it null.

Both API models' Core45 results match the
[JLL release](https://www.jll.com/en-us/newsroom/jll-arranges-sale-of-core-45-building-i-to-lba-logistics)
on LBA, South Dallas, 616,068 SF and completed sale. GPT-5 leaves the exact
closing day null. Opus 5 adds an approximate December 10 closing day, although
the participant had announced the completed sale on December 9. This precision
is unsupported by that primary source.

Opus 5's other two candidates have primary support for buyer, acquisition,
industrial use and reported aggregate size:
[Lone Star / Transwestern](https://transwestern.com/news-detail/transwestern-investment-group-acquires-380k-sf-class-a-industrial-asset-in-fort-)
(380,020 SF) and
[Midway / Ackerman](https://ackermanco.com/news/ackerman-co-acquires-12-building-258846-sf-industrial-portfolio-in-dallas-fort-worth-market/)
(258,846 SF across 12 buildings). Exact closing dates and each individual
building's minimum-size eligibility are not fully established by this audit.
The brief does not explicitly resolve portfolio versus individual-asset sizing;
that rubric ambiguity needs adjudication before a precision score is published.

## Phoenix leases: targeted financial check

GPT-5 found an actual filed Hims lease, rather than substituting a market rent.
Its $10.80/SF annual figure is the annualized scheduled base rate in
[Exhibit C](https://www.sec.gov/Archives/edgar/data/1773751/000177375125000062/hims-20241231x10kxex1012.htm).
The exhibit also conditionally abates the first seven months. The answer does
not describe that concession. This is a real executed base rate, but it must
not be presented as effective first-year cash rent or an incentive-adjusted comp.

The [Lincoln announcement](https://lpc.com/local-news/lincoln-signs-major-first-lease-at-park303-phase-2/)
supports Logisticus' 483,300 SF lease in Glendale. Its displayed date is January
28; it does not establish the exact January 21 execution day in GPT-5's row.
Earlier press coverage may establish an earlier announcement, but not execution.
The [Opus announcement](https://www.opus-group.com/News/positive-activity-at-deer-valley)
supports a signed Air2O lease for about 184,000 SF announced May 8, 2025.
Other Phoenix fields and buyer leads remain pending.

## Office refinance prospects: extension handling

Lev included Orion's 19-property office portfolio as a 2027 refinance prospect,
while correctly describing an executed extension to February 2029 in its own
answer. The [February 2026 SEC filing](https://www.sec.gov/Archives/edgar/data/1873923/000187392326000023/onl-20260217.htm)
confirms the extension, with further conditional options through August 2030.
The brief expressly requires accounting for documented extensions. This is a
qualification failure: an acknowledged historical maturity was used to retain
an ineligible result. The answer discloses its interpretation; it did not
fabricate the extension. Portfolio-versus-property eligibility is an additional
question, separate from the already decisive maturity error.

Opus 5 explicitly excluded the same Orion loan because the executed extension
moved it outside 2027. That exclusion is supported by the same filing. This is
a directly comparable qualification decision, not a complete score for either
system's returned shortlist.

GPT-5's 485 Lexington result has primary support for 935,452 SF, SL Green
sponsorship, a February 2027 maturity, and a $350 million balance as of the
January 2026 remittance period in the [KBRA surveillance release](https://www.kbra.com/publications/ygYmLFkj/kbra-downgrades-four-ratings-and-affirms-all-other-ratings-for-gsms-2017-485l).
This supports those fields at the stated reporting date, not a September 2026
balance or a full-row accuracy score.

Both Lev and GPT-5 returned 237 Park Avenue. The [August 2026 KBRA release](https://www.kbra.com/publications/JygBzSSC/kbra-affirms-all-ratings-for-mssg-2017-237p?format=web)
supports an August 2027 maturity, RXR/Walton Street sponsorship, approximately
1.3 million SF, and a stated $693.2 million whole loan. It does not label that
amount as a dated remittance balance. Lev calls it the current balance; GPT-5
leaves current balance unknown. The amount is supported as the reported whole
loan, while its balance-date precision needs qualification. Remaining fields
and the Opus 5 returned office candidates require review before an aggregate score.

## Publication rule

These are source-linked diagnostic findings. They do not establish web-wide
recall, complete candidate precision, contact deliverability, present buying
intent, lender approval, or lead conversion. No aggregate research winner is
published until the full returned set is audited under an adjudicated rubric.
