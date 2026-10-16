import pandas as pd
from sqlalchemy import create_engine
from database import get_connection





#columns to be selected from the diabetic_data.csv file
selected_columns = ['encounter_id',
        'patient_nbr',
        'age',
        'time_in_hospital',
        'number_inpatient',
        'number_emergency',
        'number_outpatient',
        'num_medications',
        'num_lab_procedures',
        'discharge_disposition_id',
        'admission_type_id',
        'readmitted']

# load selected data from diabetic_data.csv , filter for required columns, and cast column types.
def load_diabetic_data():
    #if csv file does not exist, raise an error
    try:
        # Load the CSV file into a DataFrame
        df = pd.read_csv('data/diabetic_data.csv')
    except FileNotFoundError:
        raise FileNotFoundError("The file 'data/diabetic_data.csv' does not exist.")

    # Select the required columns
    df = df[selected_columns]
    # cast the columns to the appropriate data types
   
    df = cast_columns(df)
    print(f"Data loaded and columns casted successfully. {df}")
    return df



def cast_columns(df):
        
        df['encounter_id'] = df['encounter_id'].astype(int)
        df['patient_nbr'] = df['patient_nbr'].astype(int)
        df['age'] = df['age'].astype(str)
        df['time_in_hospital'] = df['time_in_hospital'].astype(int)
        df['num_lab_procedures'] = df['num_lab_procedures'].astype(int)
        df['num_medications'] = df['num_medications'].astype(int)
        df['number_outpatient'] = df['number_outpatient'].astype(int)
        df['number_emergency'] = df['number_emergency'].astype(int)
        df['number_inpatient'] = df['number_inpatient'].astype(int)
        df['discharge_disposition_id'] = df['discharge_disposition_id'].astype(int)
        df['admission_type_id'] = df['admission_type_id'].astype(int)
        df['readmitted'] = df['readmitted'].astype(str)
        return df

#get data from load_diabetic_data() and insert into the database
#modulaise this function to load json as seperate function, get connection string as seperate function, and insert data into the database as seperate function
#before writing data into the database, check if the data already exists, if it does, clear the data and rewrite the data into the database, if it does not exist, write the data into the database
def write_data_into_db(df):
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return

    try:
        # create a cursor object to execute SQL queries
        with conn.cursor() as cursor:
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM patient_encounters")
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.execute("DELETE FROM patient_encounters")
                conn.commit()
                print("Existing data cleared from patient_encounters table.")

            # Insert data along with risk score and risk level into the patient_encounters table
            for index, row in df.iterrows():
                insert_query = """
                    INSERT INTO patient_encounters (encounter_id, patient_nbr, age, time_in_hospital, number_inpatient, number_emergency, number_outpatient, num_medications, num_lab_procedures, discharge_disposition_id, admission_type_id, readmitted, risk_score, risk_level)
                    VALUES (%s, %s, %s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    row['encounter_id'],
                    row['patient_nbr'],
                    row['age'],
                    row['time_in_hospital'],
                    row['number_inpatient'],
                    row['number_emergency'],
                    row['number_outpatient'],
                    row['num_medications'],
                    row['num_lab_procedures'],
                    row['discharge_disposition_id'],
                    row['admission_type_id'],
                    row['readmitted'],
                    row['risk_score'],
                    row['risk_level']
                ))
            conn.commit()
            print("Data inserted successfully into patient_encounters table.")
    except Exception as e:
        print("Error inserting data into the database:", e)
    finally:
        conn.close()



#Risk level mapping: 0–2 = LOW | 3–4 = MEDIUM | 5+ = HIGH
# return risk score as integer and risk level as varchar to be returned to the database
# let return be dictionary with keys risk_score and risk_level
def calculate_risk(row) -> dict:
    risk_score = 0

    if row['number_inpatient'] >= 3:
        risk_score += 3
    if row['number_emergency'] >= 2:
        risk_score += 2
    if row['number_outpatient'] >= 3:
        risk_score += 1
    if row['time_in_hospital'] >= 7:
        risk_score += 1
    if row['num_medications'] >= 20:
        risk_score += 1

    if risk_score >= 5:
        
        return {'risk_score': risk_score, 'risk_level': 'HIGH'}
    elif risk_score >= 3:
        return {'risk_score': risk_score, 'risk_level': 'MEDIUM'}
    else:
        return {'risk_score': risk_score, 'risk_level': 'LOW'}


def insert_data_into_db():
    df = load_diabetic_data()
    df = cast_columns(df)
    
    # for each row in the dataframe, convert it to dictinary and then  calculate risk score and risk level and add to the dataframe as new columns
    #comment below code to do one row at a time and write to the database, uncomment below code to do all rows at once and write to the database    
    
    for index, row in df.iterrows():
        risk = calculate_risk(row.to_dict())
        #print the risk score and risk level for each row
        print(f"Row {index}: Risk Score: {risk['risk_score']}, Risk Level: {risk['risk_level']}")
        #add risk score and risk level to the dataframe
        df.at[index, 'risk_score'] = risk['risk_score']
        df.at[index, 'risk_level'] = risk['risk_level']
    #return the dataframe with new columns risk_score and risk_level
    #print the dataframe to verify the new columns are added correctly
    print(f"Dataframe with risk score and risk level calculated: {df}")
    write_data_into_db(df)
    return(f"Dataframe with risk score and risk level calculated: {df}")


#verify if write_data_into_db() is working by calling it and checking if the data is written into the database
if __name__ == "__main__":
    insert_data_into_db()



#write function to Use this pattern:

#Read encounter IDs from patient_encounters.##
#Insert into care_interventions with INSERT ... SELECT.
##Skip rows that already exist to avoid duplicates.

def write_care_interventions():
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return

    try:
        with conn.cursor() as cursor:
            # Insert into care_interventions from patient_encounters, skipping duplicates
            insert_query = """
                INSERT INTO care_interventions (encounter_id, intervention_status, assigned_to, notes, created_at, updated_at)
                SELECT encounter_id, 'PENDING_REVIEW', 'Unassigned', '', NOW(), NOW()
                FROM patient_encounters
                WHERE encounter_id NOT IN (SELECT encounter_id FROM care_interventions)
            """
            cursor.execute(insert_query)
            conn.commit()
            print("Data inserted successfully into care_interventions table.")
    except Exception as e:
        print("Error inserting data into the database:", e)
    finally:
        conn.close()



