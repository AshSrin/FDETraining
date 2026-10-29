# implement fastapi endpoint to get the carequeue from service.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from service import (
    get_carequeue,
    get_high_risk_carequeue,
    get_all_encounters,
    get_encounter,
    get_operational_summary_service,
    patch_care_intervention,
    get_readmission_analysis_service,
    create_encounter_service,
    get_encounter_id_service,
)
from models import PatientEncounter, PatientEncounterCreate, CareInterventionPatch



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/careQueue")
def care_queue(limit: int = Query(default=100, ge=1, le=1000)):
    try:
        carequeue = get_carequeue(limit=limit)
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


@app.get("/encounters/patient/{patient_nbr}")
def get_encounter_by_patient_nbr_route(patient_nbr: int):
    try:
        encounter_id = get_encounter_id_service(patient_nbr)
        return {
            "patient_nbr": patient_nbr,
            "encounter_id": encounter_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/encounters", response_model=PatientEncounter, status_code=201)
def create_encounter(payload: PatientEncounterCreate):
    try:
        encounter = create_encounter_service(payload.model_dump())
        return encounter
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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

@app.get("/readmission_analysis")   
def readmission_analysis():
    try:
        analysis = get_readmission_analysis_service()
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    