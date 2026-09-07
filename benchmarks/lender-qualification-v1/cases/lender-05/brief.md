You are reviewing financing fit, not making a credit decision. Use only the two provided public-source summaries and their cited authoritative pages as the fixed evidence packet. Do not treat a typical guideline as an absolute ban where the source explicitly allows exceptions. Distinguish a disclosed amount range from full eligibility and from actual approval. No outreach or CRM changes. Return a JSON object with classification, reason, source_ids (array), missing_information (array), and approved (always false unless explicit actual approval evidence exists). Use one classification from: not_eligible; amount_in_range_other_criteria_unverified; fits_disclosed_property_financial_criteria_approval_unverified; case_by_case_not_standard_stabilized; insufficient_information.

Business question: Fannie Mae conventional term-sheet fit: stabilized 3-unit residential property, LTV 60%, DSCR 1.5. No exception or other program is in the supplied source.

Evidence packet:
[
  {
    "id": "fannie-conventional",
    "title": "Fannie Mae Conventional Properties Term Sheet",
    "url": "https://multifamily.fanniemae.com/financing-options/conventional-properties-term-sheet",
    "retrieved_at": "2026-09-07",
    "publication_date": null,
    "summary": "Conventional first-lien acquisition/refinance financing for existing stabilized multifamily with at least five units. Maximum LTV 80%; minimum DSCR 1.25x. Typical stabilized occupancy is 90% for 90 days; pre-stabilized commitments can receive case-by-case consideration. Nonrecourse execution is available for most loans over $750,000 with standard carve-outs. Guidelines do not establish approval of a specific borrower."
  },
  {
    "id": "freddie-transition",
    "title": "Freddie Mac Conventional Small launch",
    "url": "https://freddiemac.gcs-web.com/news-releases/news-release-details/freddie-mac-multifamily-announces-launch-integrated-conventional/",
    "retrieved_at": "2026-09-07",
    "publication_date": "2026-04-15",
    "summary": "Freddie Mac announced Conventional Small for loans from $2 million to $10 million on April 15, 2026. Applications under the former Small Balance Loan program were accepted through April 30, 2026. The announcement does not state a complete set of current underwriting criteria or promise approval."
  }
]
