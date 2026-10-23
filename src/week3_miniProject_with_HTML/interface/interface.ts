interface careInterventionInterface{
    encounterId: number;
    interventionStatus: 'PENDING_REVIEW' |
                        'ASSIGNED' |
                        'CONTACTED' |
                        'FOLLOW_UP_SCHEDULED' |
                        'CLOSED';
    assignedTo: string;
    notes: string;



}