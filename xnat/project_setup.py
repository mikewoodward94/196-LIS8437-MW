import configparser
import logging
from pathlib import Path
import requests
import subprocess

logger = logging.getLogger(__name__)


def create_project(
    xnat_configuration: dict, xnat_uri: str, xnat_projects_uri: str
) -> None:
    """
    Creates a project within XNAT using REST API and variables set in the project's config file.
    """
    project = xnat_configuration["project"]
    payload = f"""<xnat:projectData xmlns:xnat="{xnat_projects_uri}">
    <ID>{project}</ID>
    <name>{project}</name>
    <description>This is a test project.</description>
</xnat:projectData>"""
    auth_url = f"{xnat_uri}/data/JSESSION"
    auth_data = {
        "username": xnat_configuration["user"],
        "password": xnat_configuration["password"],
    }
    response = requests.post(auth_url, data=auth_data)

    if response.status_code == 200:
        session_token = response.text
        logger.info(f"Authentication successful with session: {session_token}")
    else:
        logger.critical("Authentication failed.")
        exit()

    headers = {
        "Authorization": "Basic YWRtaW46YWRtaW4=",
        "Cookie": f"JSESSIONID={session_token}",
        "Content-Type": "application/xml",
    }
    logger.info(f"Attemping to create project: {project}")
    project_response = requests.post(xnat_projects_uri, headers=headers, data=payload)

    if project_response.status_code == 200:
        logger.info("<{project}> successfully created.")
    elif project_response.status_code == 409:
        logger.error(
            f"Failed to create <{project}> due to: {project_response.status_code}. Check if project already exists."
        )
    else:
        logger.error(
            f"Failed to create <{project}> due to: {project_response.status_code}"
        )


def push_data_to_xnat(directory_path: Path) -> int:
    """
    Pushes data to XNAT using a storescu command. This requires a flat folder structure i.e., see the xnat/data folder
    and that the Patient Comments DICOM tag i.e., (0010,4000), has its value formatted as
    "Project:ProjectA Subject:Subject001 Session:Subject001_MR1" i.e., the DICOMs will be automatically be sent to ProjectA,
    grouped into the session "Subject001_MR1" under subject "Subject001".
    """
    command = f"storescu +sd -r -aec XNAT localhost 8104 {directory_path}"
    try:
        logger.info(f"Running this command: {command}")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")
        logger.debug("Standard output:\n" + stdout)
        logger.debug("Standard error:\n" + stderr)
        return result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with return code {e.returncode}")
        logger.error("Error output:\n" + e.stderr.decode("utf-8"))
        return e.returncode, e.stdout.decode("utf-8"), e.stderr.decode("utf-8")


if __name__ == "__main__":
    logging.basicConfig(
        filename=f"{Path(__file__).parent}/xnat_import.log", level=logging.INFO
    )
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

    data_path = Path(__file__).parent / "data"
    xnat_uri = config["xnat"]["SERVER"]
    xnat_projects_uri = xnat_uri + "/data/projects"

    create_project(
        xnat_configuration=xnat_configuration,
        xnat_uri=xnat_uri,
        xnat_projects_uri=xnat_projects_uri,
    )
    if data_path.exists():
        logger.info(f"Pushing data from {data_path} to XNAT.")
        storescu_status = push_data_to_xnat(data_path)
        if storescu_status == 0:
            logger.info(
                f"Data has been pushed to XNAT. Reconfirm by checking the project's list of subjects or prearchive."
            )
        else:
            logger.error(
                f"Data push to XNAT failed with return code {storescu_status}."
            )
    else:
        logger.warning(f"Data directory does not exist: {data_path}")
