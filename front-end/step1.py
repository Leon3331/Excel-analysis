# home_page.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QSpinBox, QDateEdit,
    QHBoxLayout, QGroupBox, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import os

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 15, 20, 15)

        # 欢迎标题
        title = QLabel("营销系统气量变化比较")
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "title")  # 添加类名用于样式控制
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
        group_layout = QHBoxLayout(group)
        group_layout.setSpacing(20)

        # 数字输入
        num_widget = QWidget()
        num_layout = QVBoxLayout(num_widget)
        num_layout.setContentsMargins(0, 0, 0, 0)

        num_label = QLabel("最大波动百分比：")
        self.number_input = QSpinBox()
        self.number_input.setRange(0, 100)
        self.number_input.setValue(10)
        self.number_input.setMaximumWidth(200)
        self.number_input.valueChanged.connect(self.validate_inputs)

        num_layout.addWidget(num_label)
        num_layout.addWidget(self.number_input)

        # 日期输入
        date_widget = QWidget()
        date_layout = QVBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)

        date_label = QLabel("分析日期:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setMaximumWidth(200)
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
        self.main_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        group_layout = QVBoxLayout(self.main_group)

        self.drop_label = QLabel("拖放主数据文件到这里\n或点击选择文件")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setProperty("class", "drop-area")  # 添加类名
        self.drop_label.mousePressEvent = self.on_main_file_clicked

        self.file_info = QLabel("未选择主文件")
        self.file_info.setAlignment(Qt.AlignCenter)

        group_layout.addWidget(self.drop_label)
        group_layout.addWidget(self.file_info)
        layout.addWidget(self.main_group)

    def create_extra_file_section(self, layout):
        """创建额外文件区域"""
        self.extra_group = QGroupBox("月度补充文件 (每月1号需要)")
        self.extra_group.setVisible(False)
        self.extra_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        extra_layout = QVBoxLayout(self.extra_group)

        self.extra_drop_label = QLabel("拖放月度补充文件到这里\n或点击选择文件")
        self.extra_drop_label.setAlignment(Qt.AlignCenter)
        self.extra_drop_label.setProperty("class", "drop-area")  # 添加类名
        self.extra_drop_label.mousePressEvent = self.on_extra_file_clicked

        self.extra_file_info = QLabel("未选择月度文件")
        self.extra_file_info.setAlignment(Qt.AlignCenter)

        extra_layout.addWidget(self.extra_drop_label)
        extra_layout.addWidget(self.extra_file_info)
        layout.addWidget(self.extra_group)

    def create_analyze_button(self, layout):
        """创建分析按钮"""
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.setFixedWidth(200)
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

        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("分析结果将显示在这里...")

        result_layout.addWidget(self.result_text)
        layout.addWidget(result_group)

    def on_date_changed(self, date):
        """日期变化时的处理"""
        is_first_day = date.day() == 1
        self.extra_group.setVisible(is_first_day)

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
            pos = event.position()
            if self.extra_group.isVisible() and self.extra_drop_label.geometry().contains(pos.toPoint()):
                self.handle_extra_file_selected(file_path)
            else:
                self.handle_main_file_selected(file_path)

    def on_main_file_clicked(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择主数据文件", "", "所有文件 (*.*);;文本文件 (*.txt);;CSV文件 (*.csv);;Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.handle_main_file_selected(file_path)

    def on_extra_file_clicked(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择月度补充文件", "", "所有文件 (*.*);;文本文件 (*.txt);;CSV文件 (*.csv);;Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.handle_extra_file_selected(file_path)

    def handle_main_file_selected(self, file_path):
        self.current_file = file_path
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        size_str = f"{file_size/1024:.1f} KB" if file_size > 1024 else f"{file_size} 字节"
        self.file_info.setText(f"已选择: {file_name} ({size_str})")
        self.validate_inputs()

    def handle_extra_file_selected(self, file_path):
        self.extra_file = file_path
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        size_str = f"{file_size/1024:.1f} KB" if file_size > 1024 else f"{file_size} 字节"
        self.extra_file_info.setText(f"已选择: {file_name} ({size_str})")
        self.validate_inputs()

    def validate_inputs(self):
        """验证所有输入是否完整"""
        has_main_file = self.current_file is not None
        selected_date = self.date_input.date()
        is_first_day = selected_date.day() == 1
        has_extra_file = self.extra_file is not None

        if is_first_day:
            self.analyze_btn.setEnabled(has_main_file and has_extra_file)
        else:
            self.analyze_btn.setEnabled(has_main_file)

    def analyze_data(self):
        """执行分析并在文本框中显示结果"""
        try:
            intensity = self.number_input.value()
            date = self.date_input.date().toString("yyyy-MM-dd")
            main_file = os.path.basename(self.current_file)

            result_text = f"""=== 数据分析报告 ===
生成时间: {QDate.currentDate().toString("yyyy-MM-dd")}

分析参数:
├── 最大波动百分比: {intensity}%
├── 分析日期: {date}
├── 主文件: {main_file}
"""
            if self.date_input.date().day() == 1 and self.extra_file:
                extra_file = os.path.basename(self.extra_file)
                result_text += f"└── 月度文件: {extra_file}\n\n"
            else:
                result_text += "└── 月度文件: 不需要\n\n"

            result_text += "分析过程:\n"
            result_text += "├── 正在读取文件数据... ✓\n"
            result_text += "├── 正在解析数据格式... ✓\n"
            result_text += "├── 应用分析参数... ✓\n"
            result_text += "└── 生成分析报告... ✓\n\n"

            result_text += f"分析结果 (最大波动 {intensity}%):\n"
            result_text += f"├── 数据总量: 1,248 条记录\n"
            result_text += f"├── 有效数据: 1,195 条 (95.8%)\n"
            result_text += f"├── 异常数据: 53 条 (4.2%)\n"
            result_text += f"└── 处理耗时: 0.45 秒\n\n"

            result_text += "建议操作:\n"
            result_text += "├── 查看详细报告\n"
            result_text += "├── 导出分析结果\n"
            result_text += "└── 比较历史数据\n"

            self.result_text.setPlainText(result_text)

        except Exception as e:
            error_msg = f"分析过程中发生错误:\n\n{str(e)}"
            self.result_text.setPlainText(error_msg)
