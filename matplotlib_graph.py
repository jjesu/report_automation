"""Create images and a PDF from the input data."""
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas
import pandas as pd
import pytz
from matplotlib.axes import Axes
from reportlab.pdfgen import canvas
from typing.io import IO
from typing_extensions import Self

from qbr_generator import exceptions

MONTH_ABBREVIATIONS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
MONTH_DIGITS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']


class QBRGenerator:
    """Create images and a PDF from the input data."""

    def __init__(self: Self, cycle_times_data: List[dict], peers_data: pd.DataFrame,
                 users_data: pd.DataFrame, tenant_name: str) -> None:
        """
        Create images and a PDF from the input data.

        :param cycle_times_data: input JSON data used as data source for cycle time graph and transfer type table
        :param peers_data: input DataFrame used as data source for comparison to peers table
        :param users_data: input DataFrame used as a data source for users table
        :param tenant_name: input string used to denote the tenant name
        """
        self.cycle_times_data: List[dict] = cycle_times_data
        self.peers_data: pd.DataFrame = peers_data
        self.users_data: pd.DataFrame = users_data
        self.tenant_name: str = tenant_name
        self.cycle_time_temp_file: IO = NamedTemporaryFile(suffix=f'_{self.tenant_name}_CycleTimesGraph.png')
        self.transfer_type_table_temp_file: IO = NamedTemporaryFile(suffix=f'_{self.tenant_name}_TransferTypeTable.png')
        self.peers_table_temp_file: IO = NamedTemporaryFile(suffix=f'_{self.tenant_name}_PeersTable.png')
        self.user_table_temp_file: IO = NamedTemporaryFile(suffix=f'_{self.tenant_name}_UserTable.png')

    def create_graph(self: Self) -> str:
        """
        Create cycle times graphs for each DTL tenant per state.

        :return: cycle times graph image file
        """
        try:
            data_tuples = [tuple(row[column] for column in MONTH_ABBREVIATIONS) for row in self.cycle_times_data]
        except Exception as e:
            raise exceptions.ParseCycleTimesDataException(self.cycle_times_data) from e

        _ = QBRGenerator._create_graph_from_data_tuples(data_tuples)

        return QBRGenerator._save_figure(self.cycle_time_temp_file.name, bbox_inches='tight', dpi=300)

    def create_peers_table(self: Self) -> str:
        """
        Create comparison to peers tables for each DTL tenant per state.

        :return: comparison to peers image file
        """
        try:
            pivoted_df = self.peers_data.pivot_table(index=None, columns='month').reset_index(drop=True)
        except Exception as e:
            raise exceptions.PivotDataFrameException() from e

        table_data = QBRGenerator._create_list_from_peers_pivoted_data_frame(pivoted_df)
        QBRGenerator._create_peers_table_comparison_graph(table_data)
        return QBRGenerator._save_figure(self.peers_table_temp_file.name)

    def create_transfer_table(self: Self) -> str:
        """
        Create transfer type tables for each DTL tenant per state.

        :return: transfer type table image file
        """
        try:
            table_data = [[item[column] for column in MONTH_ABBREVIATIONS] for item in self.cycle_times_data]
            colors = ['#A6C6EF', '#FEE699', '#F4B183']

            _, ax = plt.subplots(figsize=(10, 2))

            table = ax.table(cellText=table_data, loc='center', cellLoc='center')

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 2.5)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            ax.set_xticks([])
            ax.set_yticks([])

            table.auto_set_column_width([0.2] * len(MONTH_ABBREVIATIONS))

            num_rows = len(table_data)
            num_colors = len(colors)

            for i in range(num_rows):
                color = colors[i % num_colors]
                for col_num in range(len(MONTH_ABBREVIATIONS)):
                    cell = table.get_celld()[i, col_num]
                    cell.set_facecolor(color)
                    cell.set_edgecolor('white')

        except Exception as e:
            raise exceptions.CreateTransferTableException(self.cycle_times_data) from e
        else:
            return QBRGenerator._save_figure(self.transfer_type_table_temp_file.name)

    def users_table(self: Self) -> str:
        """
        Create users tables for each DTL tenant per state.

        :return: user table image file
        """
        try:
            df = self.users_data[(self.users_data[['# Created YTD']] != 0).any(axis=1)]

            colors = ['#CCCDD0', '#E7E8E9', '#CCCDD0']
            _, ax = plt.subplots(figsize=(8, 8))

            table = ax.table(cellText=df.values, colLabels=df.columns,
                             loc='center', cellLoc='center')
            table.auto_set_column_width([0, 1, 2, 3])

            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 2)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            ax.set_xticks([])
            ax.set_yticks([])

            num_rows = len(df) + 1
            num_colors = len(colors)

            for i in range(num_rows):
                color = colors[i % num_colors]
                for col_num in range(len(df.columns)):
                    cell = table.get_celld()[i, col_num]
                    cell.set_facecolor(color)
                    cell.set_edgecolor('white')

        except Exception as e:
            raise exceptions.CreateTableFromUsersDataException() from e
        else:
            return QBRGenerator._save_figure(self.user_table_temp_file.name)

    def create_pdf(self: Self) -> str:
        """
        Consolidate all the image files created by the above methods for each DTL tenant per state.

        :return: PDF file (A dashboard consisting of cycle times graph, peers table, transfer type table and user table)
        """
        try:
            last_update_datetime = datetime.now(pytz.timezone('US/Eastern')).strftime('%b-%d-%Y')
            pdf_file_path: IO = NamedTemporaryFile(suffix=f'_{self.tenant_name}_QBR_{last_update_datetime}.pdf',
                                                   delete=False)

            dashboard_width = 900
            dashboard_height = 600

            _canvas = canvas.Canvas(pdf_file_path.name, pagesize=(dashboard_width, dashboard_height))

            image_positions = [
                (self.create_peers_table(), 50, 125, 550, 100),
                (self.create_transfer_table(), 50, 45, 550, 100),
                (self.create_graph(), 20, 205, 600, 300),
                (self.users_table(), 600, 250, 300, 280)
            ]

            for image_path, pos_x, pos_y, width, height in image_positions:
                try:
                    _canvas.drawImage(image_path, pos_x, pos_y, width, height)
                except Exception as e:
                    raise exceptions.CanvasDrawImageException(_canvas) from e

            # Save and close the canvas
            _canvas.save()

        except Exception as e:
            raise exceptions.CanvasCreatePDFException() from e
        else:
            return pdf_file_path.name

    @staticmethod
    def _create_graph_from_data_tuples(data_tuples: List[tuple]) -> Axes:
        """
        Create a graph using matplotlib from a list of data tuples.

        :param data_tuples: data to use to create the graph
        :return: matplotlib axes
        """
        try:
            transfer_type = {
                'Clear': data_tuples[0],
                'Elien': data_tuples[1],
                'Paper Lien': data_tuples[2],
            }

            month_array = np.arange(len(MONTH_ABBREVIATIONS))
            width = 0.3
            multiplier = 0

            _, ax = plt.subplots(figsize=(10, 5))

            colors = ['#A6C6EF', '#FEE699', '#F4B183']

            for i, (attribute, measurement) in enumerate(transfer_type.items()):
                offset = width * multiplier
                rectangles = ax.bar(month_array + offset, measurement, width,
                                    label=attribute, color=colors[i], zorder=2)
                ax.bar_label(rectangles, padding=3, fontsize=6)
                multiplier += 1

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            ax.tick_params(axis='both', which='both', length=0)
            ax.grid(axis='y', which='both', linestyle='-', alpha=0.2)
            ax.set_yticks(np.arange(0, 81, 10))
            ax.set_yticks(np.arange(0, 81, 2), minor=True)
            ax.yaxis.grid(True, which='minor', linestyle='-', linewidth=0.5, alpha=0.1)
            ax.set_ylabel('Days', fontsize=8)
            ax.set_title('Cycle Times')
            ax.set_xticks(month_array + width * (multiplier - 1) / 2)
            ax.set_xticklabels(MONTH_ABBREVIATIONS, fontsize=8)
            ax.legend(loc='upper right', bbox_to_anchor=(0.97, 1.06), ncols=3, fontsize=7,
                      frameon=False, handlelength=0.7)
            ax.set_ylim(0, 80)
            ax.tick_params(axis='y', labelsize=8)

        except Exception as e:
            raise exceptions.CreateGraphException(data_tuples) from e
        else:
            return ax

    @staticmethod
    def _create_peers_table_comparison_graph(table_data: list) -> None:
        try:
            colors = ['#CCCDD0', '#E7E8E9', '#CCCDD0']

            _, ax = plt.subplots(figsize=(10, 2))

            table = ax.table(cellText=table_data, loc='center', cellLoc='center')

            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 2.5)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)

            ax.set_xticks([])
            ax.set_yticks([])

            num_rows = len(table_data)
            num_colors = len(colors)

            for i in range(num_rows):
                color = colors[i % num_colors]
                for col_num in range(len(MONTH_DIGITS)):
                    cell = table.get_celld()[i, col_num]
                    cell.set_facecolor(color)
                    cell.set_edgecolor('white')

        except Exception as e:
            raise exceptions.PeersTableComparisonException() from e

    @staticmethod
    def _create_list_from_peers_pivoted_data_frame(pivoted_df: pandas.DataFrame) -> list:
        try:
            missing_columns = [col for col in MONTH_DIGITS if col not in pivoted_df.columns]
            for col in missing_columns:
                pivoted_df[col] = '0.0'

            pivoted_df = pivoted_df[MONTH_DIGITS]
            table_data = pivoted_df.values.tolist()

        except Exception as e:
            raise exceptions.CreateListPeersDataFrameException() from e
        else:
            return table_data

    @staticmethod
    def _save_figure(file_name: str, bbox_inches: str | None = None, dpi: int | None = None) -> str:
        """
        Save the current matplotlib figure to the provided file name.

        :param file_name: name of the file to save to
        :param bbox_inches: bbox_inches
        :param dpi: dpi
        :return: file name where the figure was saved
        """
        try:
            plt.savefig(file_name, bbox_inches=bbox_inches, dpi=dpi)
            plt.close()

        except Exception as e:
            raise exceptions.SavePlotFigureException(file_name) from e

        return file_name
