# excel_analyzer_app.py
import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QPushButton, QFileDialog, QLabel)
from PySide6.QtCore import Qt
import openpyxl
from openpyxl.styles import PatternFill
