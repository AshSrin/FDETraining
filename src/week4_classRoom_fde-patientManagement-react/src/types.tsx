export interface encounterInterface {
    encounter_id: number;
    patient_nbr: number;
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
    risk_score: number;
    age: string;
}           