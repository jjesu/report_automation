"""Provide tests for PDFGenerator class."""
import os
import unittest
from pathlib import Path

import pandas as pd
from typing_extensions import Self

from pdf_generator import exceptions
from pdf_generator.df_to_pdf import PDFGenerator


class TestPDFGenerator(unittest.TestCase):
    """Provide tests for PDFGenerator class."""

    test_dataframe = pd.DataFrame({
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Age': [30, 25, 40],
        'City': ['New York', 'San Francisco', 'Chicago']
    })
    test_header1_text = 'Sample Report'
    test_header2_text = 'Generated on July 18, 2023'
    test_footer_text = 'This is the footer.'
    test_header_logo = 'WV_dmv_logo.png'
    test_table_header_background_hex_color = '#4472C4'
    test_table_header_text_hex_color = '#FFFFFF'
    test_odd_row_color = '#D9E1F2'
    test_even_row_color = '#FFFFFF'

    def test_pdf_generation(self: Self) -> None:
        """Test that a PDF is generated."""
        pdf_gen = PDFGenerator(
            dataframe=self.test_dataframe,
            header1_text=self.test_header1_text,
            header2_text=self.test_header2_text,
            footer_text=self.test_footer_text,
            header_logo=Path(os.path.dirname(__file__)) / self.test_header_logo,
            table_header_background_hex_color=self.test_table_header_background_hex_color,
            table_header_text_hex_color=self.test_table_header_text_hex_color,
            odd_row_color=self.test_odd_row_color,
            even_row_color=self.test_even_row_color
        )

        output_file = pdf_gen.generate_pdf()

        with output_file.open(mode='rb') as f:
            output_bytes = f.read()

        expected_output: Path = Path(os.path.dirname(__file__)) / 'expected_output.pdf'
        with expected_output.open(mode='rb') as f:
            expected_bytes = f.read()

        self.assertEqual(len(output_bytes), len(expected_bytes))

    def test_invalid_dataframe(self: Self) -> None:
        """Test with an invalid data frame."""
        with self.assertRaises(exceptions.InvalidDataFrameException):
            pdf_gen = PDFGenerator(
                dataframe=None,
                header1_text=self.test_header1_text,
                header2_text=self.test_header2_text,
                footer_text=self.test_footer_text,
                header_logo=Path(os.path.dirname(__file__)) / self.test_header_logo,
                table_header_background_hex_color=self.test_table_header_background_hex_color,
                table_header_text_hex_color=self.test_table_header_text_hex_color,
                odd_row_color=self.test_odd_row_color,
                even_row_color=self.test_even_row_color
            )
            _ = pdf_gen.generate_pdf()

    def test_missing_logo_file(self: Self) -> None:
        """Test with a non-existent logo file."""
        with self.assertRaises(exceptions.InvalidLogoFileException):
            pdf_gen = PDFGenerator(
                dataframe=self.test_dataframe,
                header1_text=self.test_header1_text,
                header2_text=self.test_header2_text,
                footer_text=self.test_footer_text,
                header_logo=Path(os.path.dirname(__file__)) / 'non_existent_logo.png',
                table_header_background_hex_color=self.test_table_header_background_hex_color,
                table_header_text_hex_color=self.test_table_header_text_hex_color,
                odd_row_color=self.test_odd_row_color,
                even_row_color=self.test_even_row_color
            )
            _ = pdf_gen.generate_pdf()
