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
