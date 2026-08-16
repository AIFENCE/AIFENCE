#!/usr/bin/env python3
"""Core 1.8.7 presentation slide-fit/render evidence validator."""
from pathlib import Path
import argparse,json
try: import jsonschema
except Exception as e: print(f"FAIL: jsonschema unavailable: {e}"); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/'schemas'/'presentation_slide_fit_evidence.schema.json').read_text())
ap=argparse.ArgumentParser();ap.add_argument('evidence');a=ap.parse_args()
ev=json.loads(Path(a.evidence).read_text());err=[]
try: jsonschema.Draft202012Validator(SCHEMA).validate(ev)
except Exception as e: print(f'FAIL: evidence schema: {e}');raise SystemExit(1)
for s in ev['slides']:
 if not s['title_fits']: err.append(f"slide {s['slide']} title does not fit")
 if s['title_subtitle_overlap']: err.append(f"slide {s['slide']} title/subtitle overlap")
 if s['body_visual_overlap']: err.append(f"slide {s['slide']} body/visual overlap")
 if s['edge_clipping']: err.append(f"slide {s['slide']} edge clipping")
 if not s['readable']: err.append(f"slide {s['slide']} not readable")
if err: print('FAIL: '+'; '.join(err));raise SystemExit(1)
print(f"PASS: presentation slide-fit preflight slides={len(ev['slides'])}")
