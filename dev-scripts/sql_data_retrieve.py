import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
database = os.environ.get('POSTGRES_DB')
user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PW')
host = "localhost"
port = 5432

def retrieve_data_from_csc(sql_query: str) -> list:
    '''
    Returns information from csc table as specified by the sql script.
    '''
    connection = psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host=host,
        port=port)
    cursor = connection.cursor()
    cursor.execute(sql_query)
    record = cursor.fetchall()

    return(record)

if __name__ == '__main__':

    sql_query = """
    SELECT pd.patient_id, ro.order_id, rr.report_id
    FROM patient.demographics pd
    LEFT JOIN radiology.order_tbl ro ON pd.patient_id = ro.patient_id
    LEFT JOIN radiology.report rr ON ro.order_id = rr.order_id
    WHERE
        pd.dod is null
    AND
        DATE_PART('year', AGE('2024-01-01', pd.dob)) >= 18
    AND
        ro.created_date >= '2024-01-01'
    AND
        ro.created_date <= '2024-03-31'
    ORDER BY pd.patient_id ASC
    """

    data = retrieve_data_from_csc(sql_query)
    df = pd.DataFrame(data, columns=['Patient ID','Order ID', 'Report ID'])
    print(df)