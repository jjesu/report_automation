# Sharepoint 
The Sharepoint class is a Python class designed to facilitate the upload and download of files to and from a SharePoint document library. SharePoint is a popular platform for document management and collaboration within organizations.

Here's an overview of what this class does:

Initialization:

The class is initialized with several parameters related to SharePoint configuration, including client_id, client_secret, tenant_id, tenant, and site_name. These parameters are used for authentication and determining the SharePoint site's URL.
Access Token Retrieval:

The _get_access_token method is responsible for obtaining an access token for SharePoint. This token is required for making authenticated requests to SharePoint's APIs.
Download from SharePoint:

The get_sharepoint_xlsx_file_bytes method allows you to download a file from SharePoint as a bytes object. It takes a file_path parameter, which specifies the path to the file in SharePoint.

The get_sharepoint_xlsx_file_download method is similar to the previous one but downloads the file to a local temporary file and returns the file path. This is useful when you need to work with the downloaded file on the local system.

Upload to SharePoint:

The post_sharepoint_xlsx_file_bytes method allows you to upload a file to SharePoint from bytes. It takes parameters such as upload_file_path (the URL path where the file will be uploaded in SharePoint), doc_lib_name (the SharePoint document library name), subfolder_name (the name of a subfolder within the document library), and upload_content (the file content as bytes).

The post_sharepoint_xlsx_file_from_path method is similar to the previous one but allows you to upload a file from a local path. It reads the file content from the local file and then calls the post_sharepoint_xlsx_file_bytes method for the upload.

HTTP Requests:

The class utilizes the Python requests library to make HTTP requests to SharePoint's REST API endpoints. It handles authentication by including the access token in the request headers.
Logging:

The class uses a logger to record information about its operations, making it easier to track and diagnose any issues that may occur during file upload or download.

# PDFGenerator

This Python class, PDFGenerator, is designed to create a PDF document from a given Pandas DataFrame and other specified elements like headers, footers, and styling options. Here's an overview of what this class does:

Initialization:

The class is initialized with various parameters, including the input DataFrame, header texts, footer text, a header logo file path, and styling options such as colors for table headers and row backgrounds.
Configuration:

The class sets up the configuration for the PDF document, including page size and margins.
It prepares a temporary PDF file to which the generated PDF will be saved.
Table Creation:

The create_table method is responsible for creating a table from the input DataFrame and applying the specified table styles.
It sets up the table structure, including column names as the header row.
Column widths can be specified as None to dynamically adjust them.
Row heights are determined based on the content.
The table is styled with different background colors for odd and even rows, gridlines, and text alignment.
Header and Footer:

The _header and _footer methods are used to draw the header and footer on the PDF canvas.
The header typically includes texts and possibly an image logo.
The footer contains text information.
PDF Generation:

The generate_pdf method orchestrates the PDF generation process.
It checks the validity of the input DataFrame and the existence of the header logo file.
It calculates the remaining space on the page after accounting for the header and footer.
It defines a custom PageTemplate that includes the header and footer.
The table created earlier is added to the document.
The document is built, and the resulting PDF is saved to a temporary file.
Exceptions Handling:

The class includes exception handling to capture and raise exceptions in case of errors during PDF generation, such as issues with drawing on the canvas, invalid input data, or missing logo files.
