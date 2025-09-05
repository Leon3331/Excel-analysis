# excel_analyzer_app.py
import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QPushButton, QFileDialog, QLabel)
from PySide6.QtCore import Qt
import openpyxl
from openpyxl.styles import PatternFill

# === 后端逻辑层 (Business Logic Layer) ===
class ExcelAnalyzer:
    """后端服务：负责Excel分析和处理"""

    def __init__(self):
        self.red_fill = PatternFill(start_color='FFFF0000', end_color='FFFF0000', fill_type='solid')
        self.yellow_fill = PatternFill(start_color='FFFFFF00', end_color='FFFFFF00', fill_type='solid')

    def analyze_file(self, file_path):
        """分析Excel文件并高亮问题"""
        try:
            # 使用pandas读取数据
            df = pd.read_excel(file_path)

            # 使用openpyxl处理格式
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active

            problems_found = 0

            # 应用分析规则
            for index, row in df.iterrows():
                row_problems = self._check_row_problems(row)
                if row_problems:
                    problems_found += 1
                    self._highlight_row(ws, index + 2, row_problems)  # +2因为Excel从1开始且有标题行

            # 保存结果
            output_path = file_path.replace('.xlsx', '_analyzed.xlsx')
            wb.save(output_path)

            return True, f"分析完成！发现 {problems_found} 个问题。结果已保存至: {output_path}"

        except Exception as e:
            return False, f"分析失败: {str(e)}"

    def _check_row_problems(self, row):
        """检查单行数据的问题"""
        problems = []
        # 示例规则
        if pd.isna(row.get('客户名称', '')) or str(row.get('客户名称', '')).strip() == '':
            problems.append(('客户名称', '客户名称为空'))
        if row.get('销售额', 0) < 1000:
            problems.append(('销售额', '销售额过低'))
        if row.get('利润率', 0) < 0.1:
            problems.append(('利润率', '利润率过低'))
        return problems

    def _highlight_row(self, worksheet, row_num, problems):
        """高亮有问题的行"""
        for col_name, problem_desc in problems:
            # 这里需要根据列名找到对应的列号（实际项目中需要更智能的映射）
            col_mapping = {'客户名称': 1, '销售额': 2, '利润率': 3}
            if col_name in col_mapping:
                cell = worksheet.cell(row=row_num, column=col_mapping[col_name])
                cell.fill = self.red_fill
                cell.comment = openpyxl.comments.Comment(problem_desc, "Analyzer")

# === 前端界面层 (UI Layer) ===
class MainWindow(QMainWindow):
    """前端界面：负责用户交互"""

    def __init__(self):
        super().__init__()
        self.analyzer = ExcelAnalyzer()  # 创建后端实例
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Excel问题分析工具")
        self.setGeometry(100, 100, 500, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.label = QLabel("请选择要分析的Excel文件")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.btn_select = QPushButton("选择Excel文件")
        self.btn_select.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )

        if file_path:
            self.label.setText(f"正在分析: {file_path.split('/')[-1]}")
            self.status_label.setText("分析中，请稍候...")

            # 调用后端服务
            success, message = self.analyzer.analyze_file(file_path)
            self.status_label.setText(message)

# === 应用入口 ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
