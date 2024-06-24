# Summary

[//]: # (Please feel free to write down any details you'd like us to take into account here! This can be about the code itself, quirks you ran into during the assignment, notes on troubleshooting, etc.)

## Setup

No problems here, except for assuming I already had dcmtk installed which caused an error in the XNAT project data push, "storescu - command not found", which was fixed by installing dcmtk.

## Development

### Question 1 
[1] Update the existing `.gitignore` file so that Python virtual environments are **included** and the `dev-data/` directory (automatically created when you build the `196-lis8437` Docker container) is **excluded** from being pushed to GitHub.

### Answer 1
- Added dev-data to .gitignore and removed venv as requested.

### Question 2
[2] Write either (1) a SQL query that can be run in pgAdmin or an interactive shell session within the `postgres` container, or (2) a Python function that queries the tables in the PostgreSQL `csc` database and returns the `patient_id`, `order_id`, and `report_id` for patients who:
  - [ ] Are alive
  - [ ] Are 18 years old or above as of January 1st, 2024
  - [ ] Had a radiology order created between January 1st, 2024 and March 31st, 2024 (inclusive)

### Answer 2
- Opened up pgadmin to get a feel for the data and understand the schema.
- Built the SQL query here for quick testing.
- Within the dev-scripts folder I wrote a script, **sql_data_retrieve.py**, with a function that takes a sql query and returns the results from the csc database, and also showed how to put this in a pandas dataframe if preferred.
- The function uses python package psycopg2 to create the connection engine and cursor.
- Additionally, used python package "load_dotenv" to retrieve values from .env file so that this script can be put on github without giving away passwords/server details.

- With regards to the query, I used left joins to ensure that in the case of patients with multiple orders/reports, these would not be lost. Additionally, it showed that there are numerous patients with orders but no reports, potentially highlighting delays. If only entries with orders and reports was requested, the sql query could be updated to account for this, using inner joins. And if only one entry per patient was requested, again this could be achieved by adapting the sql query, for example could use "select distinct on (pd.patient_id).

### Question 3
[3] Retrieve DICOMs from any one of the subjects in the `testproject` project on XNAT and:
  - [ ] Edit the DICOM tags so that:
    - [ ] The values in the Study Date (0008,0020), Acquisition Date (0008,0022), Instance Creation Date (0008,0012), and Content Date (0008,0023) are shifted by 11 days e.g., "20240101" should become "20240112".
    - [ ] The values in the Study Time (0008,0030), Acquisition Time (0008,0032), Instance Creation Time (0008,0013), and Content Time (0008,0033) DICOM tags are removed/replaced with a blank value.
    - Replace the value in the Study Description (0008,1030) DICOM tag with "This is a test study description."
  - [ ] Push these modified DICOM files back to XNAT so that they are either (1) stored under the same Subject, but with a different Session e.g., "GSTT000001" and "SessionA", respectively, or (2) stored under a different Subject with the same Session e.g., "GSTT000001_new" and "601205b7-00d2-445b-ba30-4719dcb3f8b7", respectively.

 ### Answer 3
- Within the dev-scripts folder I created a python script, **dicom_edit.py**,for this task.
- The script works by utilising the xnat api (https://wiki.xnat.org/xnat-api/dicom-dump-service-api) to pull only the necessary DICOM tags. This approach uses a fairly unweildy url but has the advantage of only retrieving the minimal amount of data necessary. This can be seen in the function **retrieve_dicom()**.
- This function also takes in the xnat details (using configparser), and the details of subject, session, and scan you want the dicom tags for. This could be seen as a limitation as it requires you to know this information and input it to the script, but it allows for a good degree of flexibility.
- The function returs a pandas dataframe of the requested dicom headers for a particular scan.
- This dataframe is then passed to second function **edit_dicom()**. This function performs the transformations as requested. In this implementation it just uses aspects of the tag descriptions to specify which transformations (or if it recognises a date), it would be better if the tags were specified in a list. This function returns the same dataframe, just with the transfromations as specified.
- These edited dataframes of dicom headers for each scan in the session are then concatenated, using the scan as an identifier. This is then passed to the function **update_original_dicom_and_upload()**.
- The idea of this function was to be able to match up the transformed dicom tags with their original dicom files (by iterating through each file, creating a dataset using pydicom, and matching with a unique identifier from the edited dicom files) and replace the dicom tags with the new values. However I ran out of time, after setting up the iterative loop and reading of each dicom file.
- The next steps would have been, matching up the transformed dicom tags with their original dicom files, replacing the values, and then outputting these dicom files to a new folder. At this point I would have adapted and used the original upload script to push this data to xnat specifying a new session.
- Biggest issue with this implementation is that you need to have access to the original dicom files, which may not be the case. Potentially would have been easier to dump all of the dicom headers for each scan, make the transformations on the specified tags, and then output to a new dicom file for upload.

### Question 4
[4] Add Orthanc as a new service to the Docker compose file.

### Answer 4
- I added Orthanc to the compose file by following https://orthanc.uclouvain.be/book/users/docker.html
- I tested that this worked succesfully by running docker compose down, and then restarting the services. Then I logged in to Orthanc at localhost:8042 and logged in using the default username and password.