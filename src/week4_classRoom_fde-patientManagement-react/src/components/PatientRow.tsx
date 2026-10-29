import type { encounterInterface } from '../types';




interface PatientRowProps {
    encounter: encounterInterface;
}


export default function PatientRow({ encounter }: PatientRowProps) {
    return (
        <tr>
            <td>{encounter.encounter_id}</td>
            <td>{encounter.patient_nbr}</td>
            <td>{encounter.risk_level}</td>
            <td>{encounter.risk_score}</td>
            <td>{encounter.age}</td>
        </tr>
    );
}   