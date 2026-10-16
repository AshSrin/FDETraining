# implement fastapi endpoint to get the carequeue from service.py
from fastapi import FastAPI, HTTPException

from service import get_carequeue, get_high_risk_carequeue,get_all_encounters, get_encounter, get_operational_summary_service, patch_care_intervention
from models import PatientEncounter, CareInterventionPatch




app = FastAPI()


@app.get("/careQueue")
def care_queue():
    try:
        carequeue = get_carequeue()
        return carequeue
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/careQueue/highRisk")
def high_risk_care_queue():
    try:
        high_risk_carequeue = get_high_risk_carequeue()
        return high_risk_carequeue
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/encounters/{encounter_id}")
def encounter(encounter_id: str):
    try:
        encounter = get_encounter(encounter_id)
        return encounter
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/encounters")
def encounters():
    try:
        encounters = get_all_encounters()
        return encounters
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.patch("/interventions/{encounter_id}")
def update_care_intervention(encounter_id: str, payload: CareInterventionPatch):
    try:
        success = patch_care_intervention(
            encounter_id,
            payload.intervention_status,
            payload.assigned_to,
            payload.notes,
        )
        return {"success": success}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/operational_summary")
def operational_summary():
    try:
        summary = get_operational_summary_service()
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    