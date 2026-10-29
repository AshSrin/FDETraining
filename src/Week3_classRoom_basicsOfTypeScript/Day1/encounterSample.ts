interface interfaceEncounter {
    encounter_id: number;
    patient_id: number;
    risk_score: number;
    risk_level: string;
    
}
const encounters: interfaceEncounter[] = [
    {
        encounter_id: 101,
        patient_id: 1001,
        risk_score: 25,
        risk_level: "Low"
    },
    {
        encounter_id: 102,
        patient_id: 1002,
        risk_score: 75,
        risk_level: "High"
    },
    {
        encounter_id: 103,
        patient_id: 1003,
        risk_score: 50,
        risk_level: "Medium"
    }
];

// Print the hardcoded encounters
console.log("Hardcoded Encounter Data:");
console.log(encounters);