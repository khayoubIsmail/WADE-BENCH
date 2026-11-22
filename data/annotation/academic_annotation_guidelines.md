# Academic / Events Domain Annotation Guidelines

This document describes how to annotate ground-truth records for the academic events and conference call for papers (CFP) tasks in WADE‑Bench v1. Each record corresponds to a single event or conference announcement.

## General Rules

1. **Schema Compliance** — Follow the `academic_event_v1` or `conference_cfp_v1` schema definitions. Required fields must be present for each record. Optional fields should be included if available.
2. **Provenance** — For every extracted field, record the provenance (e.g., XPath or CSS selector) pointing to the source of that value in the HTML snapshot. This ensures transparency and reproducibility.
3. **Normalization** — Normalize dates to ISO 8601 format (`YYYY-MM-DD`). Normalize locations to `City, Region, Country` when possible. Normalize person and organization names to a consistent format.

## Event Records (`academic_event_v1`)

Required fields:
- `event_name`: The official name of the event.
- `event_start_date`: The start date of the event (YYYY-MM-DD).
- `event_end_date`: The end date of the event (YYYY-MM-DD). If not specified, set equal to `event_start_date`.
- `location`: The city and country where the event will take place. Use `City, Region, Country` format.
- `event_url`: The URL of the event’s detail page.

Optional fields:
- `description`: A summary or abstract of the event.
- `organizer`: The organizing institution or individual.
- `topic`: The main topic or discipline of the event.
- `registration_deadline`: The date by which participants must register (ISO 8601).
- `submission_deadline`: The date by which submissions (e.g., abstracts) are due (ISO 8601).

## Conference CFP Records (`conference_cfp_v1`)

Required fields:
- `conference_name`: The full name of the conference.
- `abstract_deadline`: Submission deadline for abstracts (ISO 8601). Leave blank if not applicable.
- `full_paper_deadline`: Submission deadline for full papers (ISO 8601). Leave blank if not applicable.
- `notification_date`: Date authors are notified of acceptance (ISO 8601).
- `conference_start_date`: Start date of the conference (ISO 8601).
- `conference_end_date`: End date of the conference (ISO 8601).
- `location`: Conference venue in `City, Region, Country` format.
- `cfp_url`: URL to the call for papers.

Optional fields:
- `topics`: Topics or themes of the conference.
- `submission_link`: Direct link for submitting papers.
- `organizer`: Organizing body or committee.

## Quality Checks

- Cross‑check dates and locations for consistency across the listing and detail pages.
- Ensure each record corresponds to a unique event or conference. Avoid duplicates.
- Verify that the provenance selectors correctly point to the source elements in the HTML snapshot.

## Examples

**Event Record Example**

```
{
  "event_name": "Oxford AI Seminar Series",
  "event_start_date": "2026-03-15",
  "event_end_date": "2026-03-15",
  "location": "Oxford, England, UK",
  "event_url": "https://www.ox.ac.uk/events/ai-seminar-series",
  "description": "A weekly seminar series on advances in artificial intelligence.",
  "organizer": "Department of Computer Science, University of Oxford",
  "topic": "Artificial Intelligence",
  "registration_deadline": "",
  "submission_deadline": ""
}
```

**Conference CFP Example**

```
{
  "conference_name": "ACM SIGGRAPH 2027",
  "abstract_deadline": "2026-12-15",
  "full_paper_deadline": "2027-01-20",
  "notification_date": "2027-03-05",
  "conference_start_date": "2027-08-12",
  "conference_end_date": "2027-08-16",
  "location": "Los Angeles, CA, USA",
  "cfp_url": "https://www.acm.org/conferences/siggraph",
  "topics": "Computer Graphics, Visualization, VR/AR",
  "submission_link": "https://submissions.siggraph.org",
  "organizer": "ACM SIGGRAPH"
}
```

Refer to these examples when annotating new events.
