# home_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QSpinBox, QDateEdit,
    QHBoxLayout, QGroupBox, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import os
import requests


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 15, 20, 15)

        # 欢迎标题
        title = QLabel("数据分析工具 - A8")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px; color: #2c3e50;")
        main_layout.addWidget(title)

        # 参数输入区域
        self.create_parameter_section(main_layout)

        # 文件区域（主文件和额外文件）
        file_layout = QHBoxLayout()
        self.create_main_file_section(file_layout)
        self.create_extra_file_section(file_layout)
        main_layout.addLayout(file_layout)

        # 分析按钮
        self.create_analyze_button(main_layout)

        # 结果展示区域
        self.create_result_section(main_layout)

        self.current_file = None
        self.extra_file = None
        self.setAcceptDrops(True)

    def create_parameter_section(self, layout):
        """创建参数输入区域"""
        group = QGroupBox("分析参数")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
            }
        """)
        group_layout = QHBoxLayout(group)
        group_layout.setSpacing(20)

        # 数字输入 - 占据一半宽度
        num_widget = QWidget()
        num_layout = QVBoxLayout(num_widget)
        num_layout.setContentsMargins(0, 0, 0, 0)

        num_label = QLabel("异常阈值 (%)")
        num_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.number_input = QSpinBox()
        self.number_input.setRange(0, 100)
        self.number_input.setValue(10)
        self.number_input.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                max-width: 200px;
            }
            QSpinBox:focus {
                border-color: #3498db;
            }
        """)
        self.number_input.valueChanged.connect(self.validate_inputs)

        num_layout.addWidget(num_label)
        num_layout.addWidget(self.number_input)

        # 日期输入 - 占据另一半宽度
        date_widget = QWidget()
        date_layout = QVBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)

        date_label = QLabel("分析日期:")
        date_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
                max-width: 200px;
            }
            QDateEdit:focus {
                border-color: #3498db;
            }
        """)
        self.date_input.dateChanged.connect(self.on_date_changed)

        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)

        # 设置等宽布局
        group_layout.addWidget(num_widget)
        group_layout.addWidget(date_widget)

        layout.addWidget(group)

    def create_main_file_section(self, layout):
        """创建主文件区域"""
        self.main_group = QGroupBox("主数据文件")
        self.main_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
            }
        """)
        self.main_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        group_layout = QVBoxLayout(self.main_group)

        self.drop_label = QLabel("拖放主数据文件到这里\n或点击选择文件")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #3498db;
                border-radius: 8px;
                padding: 40px;
                background-color: #ecf0f1;
                color: #7f8c8d;
                font-size: 14px;
                min-height: 120px;
            }
            QLabel:hover {
                background-color: #dfe6e9;
                border-color: #2980b9;
            }
        """)
        self.drop_label.mousePressEvent = self.on_main_file_clicked

        self.file_info = QLabel("未选择主文件")
        self.file_info.setAlignment(Qt.AlignCenter)
        self.file_info.setStyleSheet("font-size: 12px; color: #7f8c8d; margin: 5px;")

        group_layout.addWidget(self.drop_label)
        group_layout.addWidget(self.file_info)
        layout.addWidget(self.main_group)

    def create_extra_file_section(self, layout):
        """创建额外文件区域"""
        self.extra_group = QGroupBox("月度补充文件 (每月1号需要)")
        self.extra_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
            }
        """)
        self.extra_group.setVisible(False)
        self.extra_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        extra_layout = QVBoxLayout(self.extra_group)

        self.extra_drop_label = QLabel("拖放月度补充文件到这里\n或点击选择文件")
        self.extra_drop_label.setAlignment(Qt.AlignCenter)
        self.extra_drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #27ae60;
                border-radius: 8px;
                padding: 40px;
                background-color: #ecf0f1;
                color: #7f8c8d;
                font-size: 14px;
                min-height: 120px;
            }
            QLabel:hover {
                background-color: #dfe6e9;
                border-color: #229954;
            }
        """)
        self.extra_drop_label.mousePressEvent = self.on_extra_file_clicked

        self.extra_file_info = QLabel("未选择月度文件")
        self.extra_file_info.setAlignment(Qt.AlignCenter)
        self.extra_file_info.setStyleSheet("font-size: 12px; color: #7f8c8d; margin: 5px;")

        extra_layout.addWidget(self.extra_drop_label)
        extra_layout.addWidget(self.extra_file_info)
        layout.addWidget(self.extra_group)

    def create_analyze_button(self, layout):
        """创建分析按钮"""
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.setFixedWidth(200)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_data)
        self.analyze_btn.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.analyze_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def create_result_section(self, layout):
        """创建结果展示区域"""
        result_group = QGroupBox("分析结果")
        result_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #34495e;
            }
        """)

        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px;
                background-color: #f8f9fa;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                min-height: 150px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("分析结果将显示在这里...")

        result_layout.addWidget(self.result_text)
        layout.addWidget(result_group)

    def on_date_changed(self, date):
        """日期变化时的处理"""
        is_first_day = date.day() == 1
        self.extra_group.setVisible(is_first_day)

        # 如果不再是1号，清空额外文件
        if not is_first_day:
            self.extra_file = None
            self.extra_file_info.setText("未选择月度文件")

        self.validate_inputs()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            # 根据鼠标位置判断是拖到哪个区域
            pos = event.position()
            if self.extra_group.isVisible() and self.extra_drop_label.geometry().contains(pos.toPoint()):
                self.handle_extra_file_selected(file_path)
            else:
                self.handle_main_file_selected(file_path)

    def on_main_file_clicked(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择主数据文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.handle_main_file_selected(file_path)

    def on_extra_file_clicked(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择月度补充文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.handle_extra_file_selected(file_path)

    def handle_main_file_selected(self, file_path):
        self.current_file = file_path
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} 字节"
        self.file_info.setText(f"已选择: {file_name} ({size_str})")
        self.validate_inputs()

    def handle_extra_file_selected(self, file_path):
        self.extra_file = file_path
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} 字节"
        self.extra_file_info.setText(f"已选择: {file_name} ({size_str})")
        self.validate_inputs()

    def validate_inputs(self):
        """验证所有输入是否完整"""
        has_main_file = self.current_file is not None
        selected_date = self.date_input.date()
        is_first_day = selected_date.day() == 1
        has_extra_file = self.extra_file is not None

        # 如果是1号，需要额外文件；否则只需要主文件
        if is_first_day:
            self.analyze_btn.setEnabled(has_main_file and has_extra_file)
        else:
            self.analyze_btn.setEnabled(has_main_file)

    def analyze_data(self):
        """执行分析并在文本框中显示结果"""
        try:
            # 检查是否有主文件
            if not self.current_file:
                QMessageBox.warning(self, "警告", "请先选择主数据文件")
                return

            # 检查日期是否为1号且是否有月度文件
            selected_date = self.date_input.date()
            is_first_day = selected_date.day() == 1
            if is_first_day and not self.extra_file:
                QMessageBox.warning(self, "警告", "每月1号需要上传月度补充文件")
                return

            # 准备表单数据
            files = {
                'main_file': open(self.current_file, 'rb')
            }

            data = {
                'threshold': str(self.number_input.value()),
                'analysis_date': selected_date.toString("yyyy-MM-dd")
            }

            # 如果是1号，添加月度文件
            if is_first_day and self.extra_file:
                files['extra_file'] = open(self.extra_file, 'rb')

            # 发送请求到后端
            response = requests.post("http://127.0.0.1:5000/api/analyze", files=files, data=data)

            # 关闭文件
            for file in files.values():
                file.close()

            # 处理响应
            if response.status_code == 200:
                result = response.json()
                self.result_text.setPlainText(result.get('result_text', '分析成功'))

                # 更新阈值显示
                self.number_input.setValue(result.get('abnormal_threshold', 10))

                # 显示异常数据数量
                abnormal_count = result.get('abnormal_count', 0)
                if abnormal_count > 0:
                    self.result_text.append(f"\n发现 {abnormal_count} 条异常数据记录")
            else:
                error_msg = response.json().get('error', '未知错误')
                self.result_text.setPlainText(f"分析失败: {error_msg}")

        except Exception as e:
            error_msg = f"分析过程中发生错误:\n\n{str(e)}"
            self.result_text.setPlainText(error_msg)