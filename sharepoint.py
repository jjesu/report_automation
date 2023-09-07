"""Upload and download files from Sharepoint."""
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from aws_lambda_powertools import Logger
from typing.io import IO
from typing_extensions import Self

logger = Logger()


class Sharepoint:
    """Upload and download files from Sharepoint."""

    def __init__(self: Self, client_id: str, client_secret: str, tenant_id: str, tenant: str, site_name: str) -> None:
        """
        Upload and download files from Sharepoint.

        :param client_id: SharePoint client ID
        :param client_secret: SharePoint client secret
        :param tenant: Name of the SharePoint tenant
        :param tenant_id: SharePoint tenant ID
        """
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__tenant_id = tenant_id
        self.__tenant = tenant
        self.__site_name = site_name
        self.__site_url = f'https://{self.__tenant}.sharepoint.com/sites/{self.__site_name}'
        self.__header = {
            'Authorization': 'Bearer ' + self._get_access_token()
        }

    def _get_access_token(self: Self) -> str:
        """
        Log in to sharepoint and return an access token.

        :return: access token
        """
        data = {
            'grant_type': 'client_credentials',
            'resource': f'00000003-0000-0ff1-ce00-000000000000/{self.__tenant}.sharepoint.com@{self.__tenant_id}',
            'client_id': f'{self.__client_id}@{self.__tenant_id}',
            'client_secret': self.__client_secret,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        access_token_endpoint = f'https://accounts.accesscontrol.windows.net/{self.__tenant_id}/tokens/OAuth/2'

        logger.info(f'logging in to Sharepoint: {access_token_endpoint}')
        response = requests.post(
            access_token_endpoint,
            data=data,
            headers=headers
        )

        if response.status_code != 200:
            raise ValueError(f'Failed to get access token. Status code: {response.status_code}'
                             f'Response Body: {response.content}')

        logger.info('Successfully acquired access token from SharePoint')
        return response.json().get('access_token')

    def get_sharepoint_xlsx_file_bytes(self: Self, file_path: str) -> bytes:
        """
        Download a sharepoint file as bytes.

        :param site_name: sharepoint site name
        :param file_path: sharepoint file path
        :return: bytes
        """
        logger.info(f'downloading excel file from Sharepoint: {file_path}')
        get_url_endpoint = f"{self.__site_url}/_api/web/GetFileByServerRelativeUrl('{file_path}')/OpenBinaryStream()"
        response = requests.get(get_url_endpoint, headers=self.__header)
        if response.status_code != 200:
            raise ValueError(f'Failed to download file. Status code: {response.status_code} '
                             f'Response Body: {response.content}')

        return response.content

    def get_sharepoint_xlsx_file_download(self: Self, file_path: str) -> str:
        """
        Download a sharepoint file to a local path.

        :param site_name: sharepoint site name
        :param file_path: sharepoint file path
        :return: file path
        """
        data = self.get_sharepoint_xlsx_file_bytes(file_path)
        logger.info(f'downloaded file is {len(data)} bytes')

        temp_file: IO = NamedTemporaryFile(suffix='.xlsx', delete=False)
        with temp_file as f:
            f.write(data)

        logger.info(f'file was saved to: {temp_file.name}')
        return temp_file.name

    def post_sharepoint_xlsx_file_bytes(self: Self, upload_file_path: str,
                                        doc_lib_name: str, subfolder_name: str, upload_content: bytes) -> None:
        """
        Upload a file to Sharepoint from bytes.

        :param upload_file_path: Upload file path URL in SharePoint
        :param doc_lib_name: SharePoint library name
        :param subfolder_name: SharePoint Sub-folder name
        :param upload_content: bytes stream after required data manipulation
        """
        post_endpoint = "{}/_api/web/getfolderbyserverrelativeurl('{}/{}/')/files/add(url='{}', overwrite=true)".format(
            self.__site_url, doc_lib_name, subfolder_name, upload_file_path
        )

        logger.info('Uploading file_content to Sharepoint')

        response = requests.post(
            post_endpoint,
            headers=self.__header,
            data=upload_content
        )

        if response.status_code != 200:
            raise ValueError(f'Failed to upload file. Status code: {response.status_code} '
                             f'Response Body: {response.content}')

        logger.info('file uploaded to Sharepoint successfully')

    def post_sharepoint_xlsx_file_from_path(self: Self, upload_file_path: str,
                                            doc_lib_name: str, subfolder_name: str, file_to_upload: str) -> None:
        """
        Upload a file to Sharepoint from a local path.

        :param upload_file_path: Upload file path URL in SharePoint
        :param doc_lib_name: SharePoint library name
        :param subfolder_name: SharePoint Sub-folder name
        :param file_to_upload: local file to upload
        """
        with Path(file_to_upload).open(mode='rb') as f:
            upload_content = f.read()
        self.post_sharepoint_xlsx_file_bytes(upload_file_path, doc_lib_name, subfolder_name, upload_content)
