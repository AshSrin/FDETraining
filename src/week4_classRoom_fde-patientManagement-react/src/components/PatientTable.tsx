import type { encounterInterface } from '../types';
import PatientRow from './PatientRow';



interface PatientTableProps {
    encounter: encounterInterface[];
}

export default function PatientTable({ encounter }: PatientTableProps) {
    return (
        <table className="patient-table">
            <thead>
                <tr>
                    <th>Encounter ID</th>
                    <th>Patient Number</th>
                    <th>Risk Level</th>
                    <th>Risk Score</th>
                    <th>Age</th>
                </tr>
            </thead>
            <tbody>
                {encounter.map((encounter) => (
                    <PatientRow key={encounter.encounter_id} encounter={encounter} />
                    

        ))}

           
            </tbody>
        </table>
    );
}   