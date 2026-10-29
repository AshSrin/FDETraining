import React from 'react';
import PatientTable from './PatientTable';
import type { encounterInterface } from '../types';

interface PaginationProps {
    encounter: encounterInterface[];
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ encounter, currentPage, totalPages, onPageChange }) => {
    const handlePrevious = () => {
        if (currentPage > 1) {
            onPageChange(currentPage - 1);
        }
    };

    const handleNext = () => {
        if (currentPage < totalPages) {
            onPageChange(currentPage + 1);
        }
    };

    return (
        <div>
            <PatientTable encounter={encounter} />
            <div className="pagination">
                <button onClick={handlePrevious} disabled={currentPage === 1}>
                    Previous
                </button>
                <span>
                    Page {currentPage} of {totalPages}
                </span>
                <button onClick={handleNext} disabled={currentPage === totalPages}>
                    Next
                </button>
            </div>
        </div>
    );
};

export default Pagination;