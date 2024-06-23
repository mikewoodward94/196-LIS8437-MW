import os
import configparser
from pathlib import Path
import requests
import json
import pandas as pd
import numpy as np
from datetime import date, timedelta
import pydicom

def retrieve_dicom(xnat_configuration: dict,
                   subject_id: str,
                   session_id: str,
                   scan_id: str) -> pd.DataFrame:
    '''
    Retrieves specified dicom headers and their values from xnat.
    '''

    url = "{}/data/services/dicomdump?src=/archive/projects/{}/subjects/{}/experiments/{}/scans/{}&field=StudyDate&field=AcquisitionDate&field=InstanceCreationDate&field=ContentDate&field=StudyTime&field=AcquisitionTime&field=InstanceCreationTime&field=ContentTime&field=StudyDescription&field=SOPInstanceUID".format(
                xnat_configuration["server"],
                xnat_configuration["project"], 
                subject_id,
                session_id,
                scan_id)
    
    jsession = requests.post('{}/data/JSESSION'.format(xnat_configuration["server"]), auth=(xnat_configuration["user"], xnat_configuration["password"]))
    session = requests.Session()
    session.cookies.set("JSESSIONID", jsession.text, domain='localhost.local')

    r = session.get(url)
    json_data = json.loads(r.text)
    dicom_header = json_data['ResultSet']['Result']
    headers = pd.DataFrame(dicom_header)
    return(headers)

def edit_dicom(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Edits and returns the dicom headers as requested.
    '''
    
    df["value"] = np.where(df["desc"].str.endswith('Time'), "", df["value"])
    df["value"] = df["value"].apply(
        lambda x: (pd.to_datetime(x) + timedelta(days=11)).strftime('%Y%m%d') if pd.to_datetime(x, errors='coerce') is not pd.NaT else x)
    df["value"] = np.where(df["desc"] == "Study Description", "This is a test study description.", df["value"])
    return(df)

def update_original_dicom_and_upload(edited_df: pd.DataFrame) -> None:
    '''
    Takes the edited dicom tags, matches up and edits original dicom file.
    Uploads to XNAT
    '''
    for filename in os.listdir("xnat/data/"):
        if filename.endswith(".dcm"):
            dataset = pydicom.dcmread("xnat/data/" + filename)
            ### Pseudocode
            '''
            Match up unique identifier from edited dicom tags to relate to original dicom file
            Use this to change the relevant dicom tags
            Output these edited dicom files to a new folder
            Upload this folder to xnat specifying same subject but different session.
            '''
            


if __name__ == "__main__":

    config_path = Path("config/config.cfg")
    config = configparser.ConfigParser()
    config.read(config_path)

    xnat_configuration = {
        "server": config["xnat"]["SERVER"],
        "user": config["xnat"]["USER"],
        "password": config["xnat"]["PASSWORD"],
        "project": config["xnat"]["PROJECT"],
        "verify": False,
    }

    subject_id = "XNAT_S04255"
    session_id = "XNAT_E04257"
    scans = ["301","401","701","801"]

    edited_dicom_tags = []

    for scan in scans:
        scan_df = retrieve_dicom(xnat_configuration, subject_id, session_id, scan)
        scan_df_edited = edit_dicom(scan_df)
        scan_df_edited['scan'] = scan
        edited_dicom_tags.append(scan_df_edited)
    
    edited_dicom_tags = pd.concat(edited_dicom_tags)
    
    update_original_dicom_and_upload(edited_dicom_tags)