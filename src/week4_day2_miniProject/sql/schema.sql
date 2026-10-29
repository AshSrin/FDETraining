CREATE TABLE patient_encounters(
    encounter_id INTEGER PRIMARY KEY,
    patient_nbr INTEGER NOT NULL,
    age VARCHAR(10) NOT NULL,
    time_in_hospital INTEGER NOT NULL,
    number_inpatient INTEGER NOT NULL,
    number_emergency INTEGER NOT NULL,
    number_outpatient INTEGER NOT NULL,
    num_medications INTEGER NOT NULL,
    num_lab_procedures INTEGER NOT NULL,
    discharge_disposition_id INTEGER NOT NULL,
    admission_type_id INTEGER NOT NULL,
    readmitted VARCHAR(10) NOT NULL,
    risk_score INTEGER NOT NULL,
    risk_level VARCHAR(20) NOT NULL  
);

CREATE TABLE care_interventions(
    intervention_id SERIAL PRIMARY KEY,
    encounter_id INTEGER NOT NULL,
    intervention_status VARCHAR(30) NOT NULL DEFAULT 'PENDING_REVIEW'
        CHECK (intervention_status IN (
            'PENDING_REVIEW',
            'ASSIGNED',
            'CONTACTED',
            'FOLLOW_UP_SCHEDULED',
            'CLOSED'
        )),
    assigned_to VARCHAR(100) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


# Patch sample data into care_interventions table
{
"intervention_status": "CONTACTED",
"assigned_to": "Care Team A",
"notes": "Follow-up appointment scheduled"
}

#insert sample data into patient_encounters table
{
  "patient_nbr": 8222179,
  "age": "[0-10]",
  "time_in_hospital": 4,
  "number_inpatient": 5,
  "number_emergency": 6,
  "number_outpatient": 10,
  "num_medications": 10,
  "num_lab_procedures": 10,
  "discharge_disposition_id": 10,
  "admission_type_id": 10,
  "readmitted": "NO"
}
