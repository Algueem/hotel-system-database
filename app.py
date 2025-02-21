import sys
import mysql.connector
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QTableWidget,
                             QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QLabel, QComboBox, QDateEdit, QMessageBox, QInputDialog,
                             QFormLayout, QGroupBox, QScrollArea, QHeaderView, QListWidget, 
                             QStackedWidget, QDialog)
from PyQt5.QtCore import QDate, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from ui.dev import ConfigWindow
from ui.gerente import GerenteWindow
from ui.recepcionista import RecepcionistaWindow
from ui.cliente import ClienteWindow


class DBConnectThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def run(self):
        try:
            db = mysql.connector.connect(
                host="localhost",
                port=3306,
                user="root",
                password="admin123",
                database="hotel_db"
            )
            self.finished.emit(db)
        except mysql.connector.Error as err:
            self.error.emit(f"Erro de conexão: {err}")

# ==============================================
# JANELA PRINCIPAL
# ==============================================
class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Hoteleiro")
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.setMinimumSize(1200, 800)
        
        self.init_sistema()

    def init_sistema(self):
        self.db_thread = DBConnectThread()
        self.db_thread.finished.connect(self.on_db_connected)
        self.db_thread.error.connect(self.show_error)
        self.db_thread.start()

    def on_db_connected(self, db):
        self.db = db
        self.init_interface()

    def show_error(self, error_msg):
        QMessageBox.critical(self, "Erro", error_msg)
        sys.exit(1)

    def init_interface(self):
        menu_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(15)
        
        title = QLabel("Sistema Hoteleiro")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #2c3e50;
                margin-bottom: 30px;
                font-weight: bold;
            }
        """)
        
        botoes = [
            ("Área do Cliente", self.show_tela_cliente),
            ("Recepcionista", self.show_tela_recepcionista),
            ("Gerente", self.show_tela_gerente),
            ("Desenvolvedor", self.show_tela_config)
        ]
        layout.addWidget(title)
        for texto, slot in botoes:
            btn = QPushButton(texto)
            btn.setFixedSize(200, 40)
            btn.clicked.connect(slot)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        menu_widget.setLayout(layout)
        
        self.stacked_widget.addWidget(menu_widget)
        self.stacked_widget.addWidget(ClienteWindow(self.db))
        self.stacked_widget.addWidget(RecepcionistaWindow(self.db))
        self.stacked_widget.addWidget(GerenteWindow(self.db))
        self.stacked_widget.addWidget(ConfigWindow(self.db))
        
        self.show_tela(0)


    def show_tela_cliente(self):
        self.show_tela(1)

    def show_tela_recepcionista(self):
        self.show_tela(2)

    def show_tela_gerente(self):
        self.show_tela(3)

    def show_tela_config(self):
        self.show_tela(4)

    def show_tela(self, index):
        if index == 1:
            self.stacked_widget.widget(1).carregar_dados()
        elif index == 2:
            self.stacked_widget.widget(2).carregar_dados()
        elif index == 3:
            self.stacked_widget.widget(3).carregar_dados()
        self.stacked_widget.setCurrentIndex(index)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Adicione este estilo global no início do arquivo
    app.setStyleSheet("""
        QWidget {
            font-size: 20px;
        }
        QPushButton {
            background: #2c3e50;
            color: white;
            border-radius: 4px;
            padding: 10px 20px;
            min-width: 150px;
            font-size: 20px;
        }
        QPushButton:hover {
            background: #34495e;
        }
        QLineEdit, QDateEdit {
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        QTableWidget {
            gridline-color: #ddd;
        }
        QHeaderView::section {
            background: #f0f4f7;
            padding: 5px;
        }
        QComboBox {
        padding: 5px;
        border: 1px solid #ddd;
        border-radius: 4px;
        min-width: 120px;
        background-color: white;
        color: #333;
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left-width: 1px;
        border-left-color: #ddd;
        border-left-style: solid;
    }

    QComboBox QAbstractItemView {
        border: 1px solid #ddd;
        background-color: white;
        selection-background-color: #2c3e50; /* Cor de fundo ao selecionar */
        selection-color: white; /* Cor do texto ao selecionar */
    }

    QComboBox QAbstractItemView::item {
        padding: 5px;
        color: #333; /* Cor do texto normal */
    }

    QComboBox QAbstractItemView::item:hover {
        background-color: #f0f4f7; /* Cor de fundo ao passar o mouse */
        color: #333; /* Cor do texto ao passar o mouse */
    }
    """)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())