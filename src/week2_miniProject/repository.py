from database import get_connection


# from the table create a function to select Medium and high risk patients and return it to the GET endpoint /careQueue
def get_care_queue() -> list:
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return []

    try:
        with conn.cursor() as cursor:
            # Select patients with risk_level 'Medium' or  'High'   
            select_query = """
            SELECT *
        FROM patient_encounters
            WHERE risk_level IN ('MEDIUM', 'HIGH')
            ORDER BY risk_score DESC, encounter_id
            
            """
            cursor.execute(select_query)

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            care_queue = [dict(zip(columns, row)) for row in rows]

        
        return care_queue
    except Exception as e:
        print("Error fetching care queue:", e)
        return []
    finally:
        conn.close()

#create carequeuefunction with HIGH risk patients only and return it to the GET endpoint /careQueue/high    
def get_high_risk_care_queue() -> list:
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return []

    try:
        with conn.cursor() as cursor:
            # Select patients with risk_level 'High'   
            select_query = """
            SELECT *
            FROM patient_encounters
            WHERE risk_level = 'HIGH'
            ORDER BY risk_score DESC, encounter_id
           
            """
            cursor.execute(select_query)

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            high_risk_care_queue = [dict(zip(columns, row)) for row in rows]

        
        return high_risk_care_queue
    except Exception as e:
        print("Error fetching high risk care queue:", e)
        return []
    finally:
        conn.close()

#write function to get one encounter by encounter_id and return it to the GET endpoint /careQueue/{encounter_id}
def get_encounter_by_id(encounter_id: str) -> dict:
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return {}

    try:
        with conn.cursor() as cursor:
            # Select patient encounter by encounter_id
            select_query = """
            SELECT *
            FROM patient_encounters
            WHERE encounter_id = %s
            """
            cursor.execute(select_query, (encounter_id,))

            row = cursor.fetchone()
            if row is None:
                return {}

            columns = [column[0] for column in cursor.description]
            encounter = dict(zip(columns, row))

        
        return encounter
    except Exception as e:
        print(f"Error fetching encounter with ID {encounter_id}:", e)
        return {}
    finally:
        conn.close()    

#write function to get all encounters with encounter_id and return it to the GET endpoint /encounters
def get_all_encounters() -> list:
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return []

    try:
        with conn.cursor() as cursor:
            # Select all patient encounters
            select_query = """
            SELECT *
            FROM patient_encounters
            ORDER BY encounter_id
            """
            cursor.execute(select_query)

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            encounters = [dict(zip(columns, row)) for row in rows]

        
        return encounters
    except Exception as e:
        print("Error fetching all encounters:", e)
        return []
    finally:
        conn.close()


#write a funtion to create a patch endpoint to update the below fields of care intervention table by encounter_id and return it to the PATCH endpoint /interventions/{encounter_id}
#sample payload for the patch endpoint is {
#    "intervention_status": "CONTACTED",
#    "assigned_to": "Care Team A",
#    "notes": "Follow-up appointment scheduled"
#}
def update_care_intervention(encounter_id: str, intervention_status: str, assigned_to: str, notes: str) -> bool:
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return False

    try:
        with conn.cursor() as cursor:
            # Update care intervention fields by encounter_id
            update_query = """
            UPDATE care_interventions
            SET intervention_status = %s,
                assigned_to = %s,
                notes = %s
            WHERE encounter_id = %s
            """
            #print the update query and the values to be updated
            print("Update Query:", update_query)
            print("Values to be updated:", (intervention_status, assigned_to, notes, encounter_id))
            cursor.execute(update_query, (intervention_status, assigned_to, notes, encounter_id))
            conn.commit()

            # Check if any row was updated
            if cursor.rowcount == 0:
                return False

        
        return True
    except Exception as e:
        print(f"Error updating care intervention for encounter ID {encounter_id}:", e)
        return False
    finally:
        conn.close()



#write a function to get operational summary from the dababase and return it to the GET endpoint /operationalSummary
#outcome of operational summary should be a dictionary with the following keys and values
#total_encounters: total number of encounters in the database
# total_high_risk_encounters: total number of encounters with risk_level 'High' 
# total_medium_risk_encounters: total number of encounters with risk_level 'Medium'
# total_low_risk_encounters: total number of encounters with risk_level 'Low'
#pending interventions: total number of people from care_intervention table with intervention_status 'PENDING' and risk_level 'High' or 'Medium'

#completed interventions: total number of people from care_intervention table with intervention_status 'COMPLETED' and risk_level 'High' or 'Medium'

def get_operational_summary() -> dict:
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return {}

    try:
        with conn.cursor() as cursor:
            # Get total encounters
            cursor.execute("SELECT COUNT(*) FROM patient_encounters")
            total_encounters = cursor.fetchone()[0]

            # Get total high risk encounters
            cursor.execute("SELECT COUNT(*) FROM patient_encounters WHERE risk_level = 'HIGH'")
            total_high_risk_encounters = cursor.fetchone()[0]

            # Get total medium risk encounters
            cursor.execute("SELECT COUNT(*) FROM patient_encounters WHERE risk_level = 'MEDIUM'")
            total_medium_risk_encounters = cursor.fetchone()[0]

            # Get total low risk encounters
            cursor.execute("SELECT COUNT(*) FROM patient_encounters WHERE risk_level = 'LOW'")
            total_low_risk_encounters = cursor.fetchone()[0]

            # Get pending interventions for high and medium risk
            cursor.execute("""
                SELECT COUNT(*)
                FROM care_interventions ci
                JOIN patient_encounters pe ON ci.encounter_id = pe.encounter_id
                WHERE ci.intervention_status = 'PENDING_REVIEW' AND pe.risk_level IN ('HIGH', 'MEDIUM')
            """)
            pending_interventions = cursor.fetchall()[0]

            # Get completed interventions for high and medium risk
            cursor.execute("""
                SELECT COUNT(*)
                FROM care_interventions ci
                JOIN patient_encounters pe ON ci.encounter_id = pe.encounter_id
                WHERE ci.intervention_status = 'CLOSED' AND pe.risk_level IN ('HIGH', 'MEDIUM')
            """)
            completed_interventions = cursor.fetchall()[0]

        
        return {
            "total_encounters": total_encounters,
            "total_high_risk_encounters": total_high_risk_encounters,
            "total_medium_risk_encounters": total_medium_risk_encounters,
            "total_low_risk_encounters": total_low_risk_encounters,
            "pending_interventions": pending_interventions,
            "completed_interventions": completed_interventions,
        }
    except Exception as e:
        print("Error fetching operational summary:", e)
        return {}
    finally:
        conn.close() 
    