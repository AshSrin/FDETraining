# create function to get the carequeue from repository.py and add validation to it
from repository import (
    get_care_queue,
    get_high_risk_care_queue,
    create_encounter,
    get_all_encounters as get_all_encounters_repo,
    get_encounter_by_id,
    get_encounter_by_patient_nbr,
    get_encounter_id_by_patient_nbr,
    update_care_intervention,
    get_operational_summary,
    get_readmission_analysis,
)


def calculate_risk_for_encounter(encounter_data: dict) -> tuple[int, str]:
    risk_score = 0

    if encounter_data.get('number_inpatient', 0) >= 3:
        risk_score += 3
    if encounter_data.get('number_emergency', 0) >= 2:
        risk_score += 2
    if encounter_data.get('number_outpatient', 0) >= 3:
        risk_score += 1
    if encounter_data.get('time_in_hospital', 0) >= 7:
        risk_score += 1
    if encounter_data.get('num_medications', 0) >= 20:
        risk_score += 1

    if risk_score >= 5:
        return risk_score, 'HIGH'
    elif risk_score >= 3:
        return risk_score, 'MEDIUM'
    return risk_score, 'LOW'


def get_carequeue(limit: int = 100) -> list:
    carequeue = get_care_queue(limit=limit)
    if carequeue is None:
        raise ValueError("Carequeue not found")
    return carequeue

def get_high_risk_carequeue() -> list:
    high_risk_carequeue = get_high_risk_care_queue()
    if high_risk_carequeue is None:
        raise ValueError("High risk carequeue not found")
    return high_risk_carequeue

# write function to get one encounter by encounter_id from repository.py and add validation to it
def get_encounter(encounter_id: str) -> dict:
        encounter = get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter with ID {encounter_id} not found")
        return encounter

#write function to get all encounters from repository.py and add validation to it
def get_all_encounters(
    risk_level: str | None = None,
    patient_nbr: int | None = None,
    risk_score: int | None = None,
    limit: int | None = None,
) -> list:
    provided_filters = [
        risk_level is not None,
        patient_nbr is not None,
        risk_score is not None,
    ]
    if sum(provided_filters) > 1:
        raise ValueError("Please enter only one search criteria at a time.")

    encounters = get_all_encounters_repo(
        risk_level=risk_level,
        patient_nbr=patient_nbr,
        risk_score=risk_score,
        limit=limit,
    )
    if not encounters:
        return []
    return encounters


def get_encounters() -> list:
    encounters = get_all_encounters_repo()
    if not encounters:
        raise ValueError("No encounters found")
    return encounters


def get_encounter_id_service(patient_nbr: int) -> int:
    if patient_nbr is None:
        raise ValueError("Patient number is required")

    encounter_id = get_encounter_id_by_patient_nbr(patient_nbr)
    if encounter_id is None:
        raise ValueError(f"No encounter found for patient number {patient_nbr}")

    return encounter_id


def create_encounter_service(encounter_data: dict) -> dict:
    payload = dict(encounter_data)
    patient_nbr = int(payload.get('patient_nbr', 0))
    existing = get_encounter_by_patient_nbr(patient_nbr)
    if existing:
        raise ValueError(f"Patient number {patient_nbr} already exists in the database.")

    payload['risk_score'], payload['risk_level'] = calculate_risk_for_encounter(payload)
    payload['number_inpatient'] = int(payload.get('number_inpatient', 0))
    payload['number_emergency'] = int(payload.get('number_emergency', 0))
    payload['number_outpatient'] = int(payload.get('number_outpatient', 0))
    payload['time_in_hospital'] = int(payload.get('time_in_hospital', 0))
    payload['num_medications'] = int(payload.get('num_medications', 0))
    payload['num_lab_procedures'] = int(payload.get('num_lab_procedures', 0))
    payload['discharge_disposition_id'] = int(payload.get('discharge_disposition_id', 0))
    payload['admission_type_id'] = int(payload.get('admission_type_id', 0))
    payload['readmitted'] = str(payload.get('readmitted', 'NO'))

    created_encounter = create_encounter(payload)
    if not created_encounter:
        raise ValueError("Failed to create patient encounter")
    return created_encounter

#create a function to implement patch endpoint in repository.py
def patch_care_intervention(encounter_id: str, intervention_status: str, assigned_to: str, notes: str) -> bool:
    success = update_care_intervention(encounter_id, intervention_status, assigned_to, notes)
    if not success:
        raise ValueError(f"Failed to update care intervention for encounter ID {encounter_id}")
    return success

def get_operational_summary_service() -> dict:
    operational_summary = get_operational_summary()
    if not operational_summary:
        raise ValueError("Failed to fetch operational summary")
    return operational_summary

def get_readmission_analysis_service() -> dict:
    readmission_analysis = get_readmission_analysis()
    if not readmission_analysis:
        raise ValueError("Failed to fetch readmission analysis")
    return readmission_analysis
