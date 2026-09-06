"""Freeze an additional cohort selected by existing gateway access, before outputs."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crebench import run_pilot

# Selection is explicitly separate from the original paid-model cohort.
run_pilot.MODELS = ['xiaomi/mimo-v2.5', 'xiaomi/mimo-v2.5-pro', 'inclusionai/ling-3.0-flash-sante']
plan = run_pilot.prepare('cases/public/harbor-court-001',
                        sys.argv[1], 'work/gateway-models.json')
print({'calls': 9, 'reserved_usd': plan['cost_reservation_usd']})
