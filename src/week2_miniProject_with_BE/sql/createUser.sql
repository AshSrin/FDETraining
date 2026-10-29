CREATE DATABASE fde_DRIQ OWNER CMT;
CREATE USER care_management with password 'CMT_LOCAL_2026';

CREATE USER hospital_operations with password 'HOP_LOCAL_2026'; 

CREATE USER clinical_leadership with password 'CLD_LOCAL_2026';
CREATE USER finance_transformation with password 'FIN_LOCAL_2026';

-- 3. Allow access to the schema
GRANT USAGE ON SCHEMA public TO
    care_management,
    hospital_operations,
    clinical_leadership,
    finance_transformation;


    -- 4. Allow all four users to read both tables
GRANT SELECT ON TABLE
    public.patient_encounters,
    public.care_interventions
TO
    care_management,
    hospital_operations,
    clinical_leadership,
    finance_transformation;


-- 5. Allow Care Management to update intervention details
GRANT UPDATE (
    intervention_status,
    assigned_to,
    notes,
    updated_at
)
ON public.care_interventions
TO care_management;
