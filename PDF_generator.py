"""Create a PDF from a DataFrame and images."""
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Table, TableStyle
from typing.io import IO
from typing_extensions import Self

from pdf_generator import exceptions


class PDFGenerator:
    """Create a PDF from a DataFrame and images."""

    def __init__(self: Self, dataframe: pd.DataFrame, header1_text: str, header2_text: str, footer_text: str,
                 header_logo: Path, table_header_background_hex_color: str,
                 table_header_text_hex_color: str, odd_row_color: str, even_row_color: str) -> None:
        """
        Initialize PDFGenerator with input data and configuration.

        :param dataframe: input dataframe used as a data source
        :param header1_text: PDF header verbiage 1
        :param header2_text: PDF header verbiage 2
        :param footer_text: PDF footer verbiage
        :param header_logo: PDF header logo
        """
        self.dataframe = dataframe
        self.header1_text = header1_text
        self.header2_text = header2_text
        self.footer_text = footer_text
        self.header_logo = header_logo
        self.table_header_background_hex_color = table_header_background_hex_color
        self.table_header_text_hex_color = table_header_text_hex_color
        self.odd_row_color = odd_row_color
        self.even_row_color = even_row_color
        self.output_file: IO = NamedTemporaryFile(suffix='.pdf', delete=False)

        # Define custom page size (15x20 inches)
        self.page_width = 15 * inch
        self.page_height = 20 * inch
        self.pagesize = (self.page_width, self.page_height)

        # Create BaseDocTemplate object with custom page size.
        self.my_doc = BaseDocTemplate(
            self.output_file.name,
            pagesize=self.pagesize,
            rightMargin=0,
            leftMargin=0,
            topMargin=0,
            bottomMargin=0
        )

    def create_table(self: Self) -> Table:
        """
        Create the table and apply the specified table styles.

        :return: The table object with the specified styles.
        """
        # Create column names as the header row
        header_row = self.dataframe.columns.tolist()
        data_with_header = [header_row] + self.dataframe.values.tolist()
        data = data_with_header

        # Define column widths ("None" parameter will dynamically adjust the column width)
        c_width = None

        # Define the row heights
        row_heights = [20] * len(data)

        # Create the table with the updated rowHeights
        table = Table(data, rowHeights=row_heights, colWidths=c_width, repeatRows=1)

        # Apply table styles to the table header
        table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Align table header to the center
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.table_header_background_hex_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(self.table_header_text_hex_color)),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),  # Align header vertically
        ])

        # Set different background colors for odd and even rows
        for i in range(1, len(data)):
            if i % 2 == 0:
                bg_color = colors.HexColor(self.even_row_color)
            else:
                bg_color = colors.HexColor(self.odd_row_color)
            table_style.add('BACKGROUND', (0, i), (-1, i), bg_color)
            table_style.add('ALIGN', (0, i), (-1, i), 'LEFT')

        for i in range(0, len(data)):
            table_style.add('GRID', (0, i), (-1, i), 1, colors.black)

        table.setStyle(table_style)

        return table

    def _header(self: Self, _canvas: canvas, _: None) -> None:
        """
        Draw the header and footer on the PDF canvas.

        :param _canvas: The PDF canvas to draw on.
        """
        try:
            _canvas.saveState()
            _canvas.setFont('Helvetica-Bold', 18)
            _canvas.setFillColor(colors.HexColor('#002060'))
            header_text_width = _canvas.stringWidth(self.header1_text, 'Helvetica-Bold', 18)
            x_pos = (self.page_width - header_text_width) / 2  # Calculate x-coordinate for center alignment
            _canvas.drawString(x_pos, self.page_height - 0.70 * inch, self.header1_text)

            # Calculate x-coordinate for center alignment of the Updated text
            updated_text = self.header2_text
            updated_text_width = _canvas.stringWidth(updated_text, 'Helvetica-Bold', 18)
            x_updated = (self.page_width - updated_text_width) / 2
            _canvas.drawString(x_updated, self.page_height - 1.05 * inch, updated_text)

            _canvas.drawImage(
                str(self.header_logo), 1.25 * inch, self.page_height - (1.3 * inch), width=2.0 * inch, height=1.0 * inch
            )
            _canvas.setFont('Helvetica-Bold', 8)
            _canvas.restoreState()
        except Exception as e:
            raise exceptions.DrawCanvasException('header') from e

    def _footer(self: Self, _canvas: canvas, _: None) -> None:
        """
        Draw the footer on the PDF canvas.

        :param _canvas: The PDF canvas to draw on.
        """
        try:
            _canvas.saveState()
            _canvas.setFont('Helvetica-Bold', 10)
            footer_text = self.footer_text

            # Calculate the width of the footer text
            footer_text_width = _canvas.stringWidth(footer_text, 'Helvetica', 10)

            # Calculate the x-coordinate for center alignment of the footer text
            x_footer = (self.page_width - footer_text_width) / 2
            _canvas.drawString(x_footer, 0.1 * inch, footer_text)

            _canvas.restoreState()
        except Exception as e:
            raise exceptions.DrawCanvasException('footer') from e

    def generate_pdf(self: Self) -> Path:
        """Generate the complete PDF document with the specified table styles, header, and footer."""
        if not isinstance(self.dataframe, pd.DataFrame) or self.dataframe.empty:
            raise exceptions.InvalidDataFrameException(self.dataframe)

        if not self.header_logo.exists():
            raise exceptions.InvalidLogoFileException(self.header_logo)

        try:
            # Calculate the remaining height for the header and footer
            header_footer_height = 1.25 * inch  # Adjust this value as needed
            remaining_height = self.page_height - header_footer_height

            # Create a custom PageTemplate for the header and footer
            main_frame = Frame(0, 0, self.page_width, remaining_height, id='main_frame', showBoundary=0)
            main_template = PageTemplate(id='main_template', frames=[main_frame], onPage=self._header,
                                         onPageEnd=self._footer)

            # Add the PageTemplates to the BaseDocTemplate
            self.my_doc.addPageTemplates(main_template)

            # Create the table
            table = self.create_table()

            # Build the document
            self.my_doc.build([table])

        except Exception as e:
            raise exceptions.GeneratePDFException() from e
        else:
            return Path(self.output_file.name)
