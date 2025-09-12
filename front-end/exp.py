import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QStackedWidget, QLabel
)
from PySide6.QtCore import Qt
from home import HomePage

class NavigationBar(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # 存储所有按钮的引用
        self.buttons = []

        # 设置导航栏样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-bottom: 1px solid #cccccc;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                background-color: transparent;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #d0d0d0;
                color: #0066cc;
                border-bottom: 2px solid #0066cc;
            }
        """)

    def add_button(self, text):
        button = QPushButton(text)
        button.setCheckable(True)
        self.layout.addWidget(button)
        self.buttons.append(button)
        return button

    def set_active_button(self, active_button):
        """设置活动的按钮，取消其他所有按钮的选中状态"""
        for button in self.buttons:
            button.setChecked(button is active_button)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("销售部excel辅助分析软件")
        self.setGeometry(100, 100, 800, 600)

        # 创建中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建导航栏
        self.nav_bar = NavigationBar()
        main_layout.addWidget(self.nav_bar)

        # 创建堆叠窗口部件用于显示不同页面
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # 创建页面和导航按钮
        self.pages = {}
        self.setup_pages()

    def setup_pages(self):
        # 定义页面名称和对应的创建函数
        page_definitions = [
            ("A8", self.create_home_page),
        ]

        for i, (name, creator) in enumerate(page_definitions):
            # 创建导航按钮
            button = self.nav_bar.add_button(name)

            # 创建页面
            page = creator()
            self.stacked_widget.addWidget(page)
            self.pages[name] = page

            # 连接按钮点击事件
            button.clicked.connect(lambda idx=i, btn=button: self.switch_page(idx, btn))

            # 设置第一个按钮为选中状态
            if i == 0:
                button.setChecked(True)

    def switch_page(self, index, button):
        # 切换页面
        self.stacked_widget.setCurrentIndex(index)

        # 更新按钮选中状态
        self.nav_bar.set_active_button(button)

    def create_home_page(self):
        return HomePage()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
