from pydantic import BaseModel

# this is my table, add models for the table
#CREATE TABLE patient_encounters(
class PatientEncounter(BaseModel):
    encounter_id: int
    patient_nbr: int
    age: str
    time_in_hospital: int
    number_inpatient: int
    number_emergency: int
    number_outpatient: int
    num_medications: int
    num_lab_procedures: int
    discharge_disposition_id: int
    admission_type_id: int
    readmitted: str
    risk_score: int
    risk_level: str

#this is my care_intervention table, add models for the table
class CareIntervention(BaseModel):  
    intervention_id: int
    encounter_id: int
    intervention_status: str
    assigned_to: str
    notes: str
    created_at: str
    updated_at: str


class CareInterventionPatch(BaseModel):
    intervention_status: str
    assigned_to: str
    notes: str

  
    