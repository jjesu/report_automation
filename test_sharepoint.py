"""Provide tests for Sharepoint class."""
import os
import unittest
from pathlib import Path

import responses
from responses import matchers
from typing_extensions import Self

from sharepoint import Sharepoint


class TestSharepoint(unittest.TestCase):
    """Provide tests for Sharepoint class."""

    test_client_id = 'xxxxxxxxx'
    test_client_secret = 'yyyyyyyy'
    test_tenant = 'test'
    test_tenant_id = 'test'
    test_site_name = 'test_site'
    test_file_path = 'test_file.xlsx'
    test_site_url = f'https://{test_tenant}.sharepoint.com/sites/{test_site_name}'
    test_url_endpoint = f'https://accounts.accesscontrol.windows.net/{test_tenant_id}/tokens/OAuth/2'
    test_get_url_endpoint = f"{test_site_url}/_api/web/GetFileByServerRelativeUrl('{test_file_path}')/OpenBinaryStream()"
    test_doc_lib_name = 'documents'
    test_subfolder_name = 'Executive Reporting'
    test_upload_file_path = '/sites/ReportAutomation/Shared%20Documents/Executive%20Reporting/DTRS_weekly_stats.xlsx'
    test_post_url_endpoint = "{}/_api/web/getfolderbyserverrelativeurl('{}/{}/')/files/add(url='{}', overwrite=true)".format(
        test_site_url, test_doc_lib_name, test_subfolder_name, test_upload_file_path
    )

    def setUp(self: Self) -> None:
        """Set up test dependencies."""
        test_file = Path(os.path.dirname(__file__)) / self.test_file_path
        with test_file.open(mode='rb') as f:
            self.test_file_bytes = f.read()

    @responses.activate
    def test_get_sharepoint_xlsx_file_bytes(self: Self) -> None:
        """Test that bytes stream is returned when retrieving a file from sharepoint."""
        # Mock the login request and return an ID token
        responses.add(responses.POST,
                      self.test_url_endpoint,
                      json={'access_token': 'test_token'},
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Content-Type': 'application/x-www-form-urlencoded'
                          })
                      ])

        sharepoint = Sharepoint(self.test_client_id, self.test_client_secret, self.test_tenant, self.test_tenant_id,
                                self.test_site_name)

        # Mock get sharepoint file request and return file content
        responses.add(responses.GET,
                      self.test_get_url_endpoint,
                      body=self.test_file_bytes,
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Authorization': 'Bearer test_token'
                          })
                      ])
        bytes_stream = sharepoint.get_sharepoint_xlsx_file_bytes(self.test_file_path)
        self.assertEqual(self.test_file_bytes, bytes_stream)

    @responses.activate
    def test_class_creation_throws_exception_on_login(self: Self) -> None:
        """Test that an exception is thrown when the class is instantiated."""
        # Mock the login request and return an HTTP 401 error
        responses.add(responses.POST,
                      self.test_url_endpoint,
                      body='invalid credentials',
                      status=401,
                      match=[
                          matchers.header_matcher({
                              'Content-Type': 'application/x-www-form-urlencoded'
                          })
                      ])
        # Make sure the class throws an exception when called because the login failed
        with self.assertRaises(ValueError):
            Sharepoint(self.test_client_id, self.test_client_secret, self.test_tenant, self.test_tenant_id,
                       self.test_site_name)

    @responses.activate
    def test_get_sharepoint_xlsx_file_bytes_throws_exception_on_file_retrieval(self: Self) -> None:
        """Test that an exception is thrown when querying a card returns an error."""
        # Mock the login request and return an ID token
        responses.add(responses.POST,
                      self.test_url_endpoint,
                      json={'access_token': 'test_token'},
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Content-Type': 'application/x-www-form-urlencoded'
                          })
                      ])

        sharepoint = Sharepoint(self.test_client_id, self.test_client_secret, self.test_tenant, self.test_tenant_id,
                                self.test_site_name)

        # Mock the get sharepoint file request and return an HTTP 404 Not Found error
        responses.add(responses.GET,
                      self.test_get_url_endpoint,
                      body='not found',
                      status=404,
                      match=[
                          matchers.header_matcher({
                              'Authorization': 'Bearer test_token'
                          })
                      ])

        # Make sure the method throws an exception when called because the file request failed
        with self.assertRaises(ValueError):
            sharepoint.get_sharepoint_xlsx_file_bytes(self.test_file_path)

    @responses.activate
    def test_post_sharepoint_xlsx_file_bytes(self: Self) -> None:
        """Test that a bytes stream is uploaded when posting a file to sharepoint."""
        # Mock the login request and return an ID token
        responses.add(responses.POST,
                      self.test_url_endpoint,
                      json={'access_token': 'test_token'},
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Content-Type': 'application/x-www-form-urlencoded'
                          })
                      ])

        sharepoint = Sharepoint(self.test_client_id, self.test_client_secret, self.test_tenant, self.test_tenant_id,
                                self.test_site_name)

        # Mock post file request and upload file to sharepoint
        responses.add(responses.POST,
                      self.test_post_url_endpoint,
                      body=self.test_file_bytes,
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Authorization': 'Bearer test_token'
                          })
                      ])

        sharepoint.post_sharepoint_xlsx_file_bytes(self.test_upload_file_path, self.test_doc_lib_name,
                                                   self.test_subfolder_name,
                                                   self.test_file_bytes)

    @responses.activate
    def test_post_sharepoint_xlsx_file_bytes_throws_exception_on_file_upload(self: Self) -> None:
        """Test that an exception is thrown when the upload request fails."""
        # Mock the login request and return an ID token
        responses.add(responses.POST,
                      self.test_url_endpoint,
                      json={'access_token': 'test_token'},
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Content-Type': 'application/x-www-form-urlencoded'
                          })
                      ])

        sharepoint = Sharepoint(self.test_client_id, self.test_client_secret, self.test_tenant, self.test_tenant_id,
                                self.test_site_name)

        # Mock post file request and upload file to sharepoint
        responses.add(responses.POST,
                      self.test_post_url_endpoint,
                      status=401,
                      match=[
                          matchers.header_matcher({
                              'Authorization': 'Bearer test_token'
                          })
                      ])

        # Make sure the method throws an exception when called because the file request failed
        with self.assertRaises(ValueError):
            sharepoint.post_sharepoint_xlsx_file_bytes(self.test_upload_file_path, self.test_doc_lib_name,
                                                       self.test_subfolder_name,
                                                       b'test')

    @responses.activate
    def test_get_sharepoint_xlsx_file_download(self: Self) -> None:
        """Test that a file path is returned when retrieving a file from sharepoint."""
        # Mock the login request and return an ID token
        responses.add(responses.POST,
                      self.test_url_endpoint,
                      json={'access_token': 'test_token'},
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Content-Type': 'application/x-www-form-urlencoded'
                          })
                      ])

        sharepoint = Sharepoint(self.test_client_id, self.test_client_secret, self.test_tenant, self.test_tenant_id,
                                self.test_site_name)

        # Mock get sharepoint file request and return file content
        responses.add(responses.GET,
                      self.test_get_url_endpoint,
                      body=self.test_file_bytes,
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Authorization': 'Bearer test_token'
                          })
                      ])
        sharepoint_file = sharepoint.get_sharepoint_xlsx_file_download(self.test_file_path)
        with Path(sharepoint_file).open(mode='rb') as f:
            result_bytes = f.read()
        self.assertEqual(self.test_file_bytes, result_bytes)

    @responses.activate
    def test_post_sharepoint_xlsx_file_from_path(self: Self) -> None:
        """Test that a local file is uploaded when posting a file to sharepoint."""
        # Mock the login request and return an ID token
        responses.add(responses.POST,
                      self.test_url_endpoint,
                      json={'access_token': 'test_token'},
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Content-Type': 'application/x-www-form-urlencoded'
                          })
                      ])

        sharepoint = Sharepoint(self.test_client_id, self.test_client_secret, self.test_tenant, self.test_tenant_id,
                                self.test_site_name)

        # Mock post file request and upload file to sharepoint
        responses.add(responses.POST,
                      self.test_post_url_endpoint,
                      body=self.test_file_bytes,
                      status=200,
                      match=[
                          matchers.header_matcher({
                              'Authorization': 'Bearer test_token'
                          })
                      ])

        sharepoint.post_sharepoint_xlsx_file_from_path(self.test_upload_file_path, self.test_doc_lib_name,
                                                       self.test_subfolder_name,
                                                       os.path.join(os.path.dirname(__file__), self.test_file_path))
