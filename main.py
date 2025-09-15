# excel_analyzer_app.py
import sys
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QPushButton, QFileDialog, QLabel)
from PySide6.QtCore import Qt
import openpyxl
from openpyxl.styles import PatternFill

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar,
                               QPushButton, QWidget, QVBoxLayout, QLabel, QSizePolicy)
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt-Material 导航条示例")
        self.resize(800, 600)

        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 添加一些内容到中央区域
        label = QLabel("🎉 欢迎使用 Material Design 风格的导航条！\n\n尝试点击上面的导航按钮。")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # 创建导航工具栏
        self.setup_toolbar()

    def setup_toolbar(self):
        """创建并设置导航工具栏"""
        toolbar = QToolBar("主导航")
        toolbar.setMovable(False)  # 禁止移动工具栏
        self.addToolBar(toolbar)

        # 创建导航按钮
        home_btn = QPushButton("🏠 首页")
        home_btn.clicked.connect(self.on_home_clicked)

        explore_btn = QPushButton("🔍 探索")
        explore_btn.clicked.connect(self.on_explore_clicked)

        messages_btn = QPushButton("✉️ 消息")
        messages_btn.clicked.connect(self.on_messages_clicked)

        profile_btn = QPushButton("👤 我的")
        profile_btn.clicked.connect(self.on_profile_clicked)

        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.clicked.connect(self.on_settings_clicked)

        # 将按钮添加到工具栏
        toolbar.addWidget(home_btn)
        toolbar.addWidget(explore_btn)
        toolbar.addWidget(messages_btn)
        toolbar.addWidget(profile_btn)
        toolbar.addWidget(settings_btn)

        # 添加弹性空间使按钮靠左对齐
        toolbar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # 可以添加右侧的按钮（如搜索、通知等）
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self.on_search_clicked)
        toolbar.addWidget(search_btn)

    def on_home_clicked(self):
        print("首页按钮被点击")

    def on_explore_clicked(self):
        print("探索按钮被点击")

    def on_messages_clicked(self):
        print("消息按钮被点击")

    def on_profile_clicked(self):
        print("我的按钮被点击")

    def on_settings_clicked(self):
        print("设置按钮被点击")

    def on_search_clicked(self):
        print("搜索按钮被点击")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 应用 qt-material 主题
    # 可选主题: 'dark_blue.xml', 'light_blue.xml', 'dark_cyan.xml', 'light_cyan.xml' 等
    apply_stylesheet(app, theme='dark_blue.xml')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
