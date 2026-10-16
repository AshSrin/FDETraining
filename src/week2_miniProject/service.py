# create function to get the carequeue from repository.py and add validation to it
from repository import get_care_queue, get_high_risk_care_queue


def get_carequeue() -> list:
    carequeue = get_care_queue()
    if carequeue is None:
        raise ValueError("Carequeue not found")
    return carequeue

def get_high_risk_carequeue() -> list:
    high_risk_carequeue = get_high_risk_care_queue()
    if high_risk_carequeue is None:
        raise ValueError("High risk carequeue not found")
    return high_risk_carequeue

# write function to get one encounter by encounter_id from repository.py and add validation to it
from repository import get_encounter_by_id      
def get_encounter(encounter_id: str) -> dict:
        encounter = get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter with ID {encounter_id} not found")
        return encounter

#write function to get all encounters from repository.py and add validation to it
from repository import get_all_encounters
def get_encounters() -> list:
    encounters = get_all_encounters()
    if not encounters:
        raise ValueError("No encounters found")
    return encounters

#create a function to implement patch endpoint in repository.py
from repository import update_care_intervention
def patch_care_intervention(encounter_id: str, intervention_status: str, assigned_to: str, notes: str) -> bool:
    success = update_care_intervention(encounter_id, intervention_status, assigned_to, notes)
    if not success:
        raise ValueError(f"Failed to update care intervention for encounter ID {encounter_id}")
    return success

from repository import get_operational_summary
def get_operational_summary_service() -> dict:
    operational_summary = get_operational_summary()
    if not operational_summary:
        raise ValueError("Failed to fetch operational summary")
    return operational_summary