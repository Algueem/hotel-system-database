import mysql.connector
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QTableWidget,
                             QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QLabel, QComboBox, QDateEdit, QMessageBox, QInputDialog,
                             QFormLayout, QGroupBox, QScrollArea, QHeaderView, QListWidget, 
                             QStackedWidget, QDialog)
from PyQt5.QtCore import QDate, QThread, pyqtSignal
from PyQt5.QtGui import QIntValidator, QDoubleValidator

class ClienteWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.setMinimumSize(800, 600)

    def initUI(self):
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        btn_voltar = QPushButton("← Voltar ao Menu")
        btn_voltar.clicked.connect(self.voltar_menu)
        header.addWidget(btn_voltar)
        header.addStretch()
        # Campo de busca
        search_layout = QHBoxLayout()
        self.txt_cpf = QLineEdit()
        self.txt_cpf.setPlaceholderText("Digite o CPF (somente números)")
        self.txt_cpf.setInputMask("999.999.999-99")
        btn_buscar = QPushButton("Buscar Reservas")
        btn_buscar.clicked.connect(self.buscar_reservas)
        
        search_layout.addWidget(QLabel("CPF:"))
        search_layout.addWidget(self.txt_cpf)
        search_layout.addWidget(btn_buscar)
        
        # Tabela de resultados
        self.tbl_reservas = QTableWidget()
        self.tbl_reservas.setColumnCount(6)
        self.tbl_reservas.setHorizontalHeaderLabels(
            ["ID", "Quarto", "Check-in", "Check-out", "Status", "Valor Total"]
        )
        self.tbl_reservas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addLayout(header)
        layout.addLayout(search_layout)
        layout.addWidget(self.tbl_reservas)
        self.setLayout(layout)

    def voltar_menu(self):
        self.parent().setCurrentIndex(0)

    def carregar_dados(self):
        self.txt_cpf.clear()
        self.tbl_reservas.setRowCount(0)

    def buscar_reservas(self):
        cpf = self.txt_cpf.text().replace(".", "").replace("-", "")
        if len(cpf) != 11:
            QMessageBox.warning(self, "Aviso", "CPF inválido!")
            return

        try:
            cursor = self.db.cursor()
            query = """
                SELECT r.idReserva, q.numero_quarto, r.data_inicio, r.data_fim, 
                       q.status, p.valor
                FROM Reserva r
                JOIN Quarto q ON r.idQuarto = q.numero_quarto
                JOIN Pagamento p ON r.idReserva = p.idReserva
                WHERE r.CPF_cliente = %s
                GROUP BY r.idReserva
            """
            cursor.execute(query, (cpf,))
            self.popular_tabela(cursor.fetchall())
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar reservas:\n{err}")

    def popular_tabela(self, dados):
        self.tbl_reservas.setRowCount(len(dados))
        for row, (id_reserva, quarto, inicio, fim, status, total) in enumerate(dados):
            self.tbl_reservas.setItem(row, 0, QTableWidgetItem(str(id_reserva)))
            self.tbl_reservas.setItem(row, 1, QTableWidgetItem(str(quarto)))
            self.tbl_reservas.setItem(row, 2, QTableWidgetItem(inicio.strftime("%d/%m/%Y")))
            self.tbl_reservas.setItem(row, 3, QTableWidgetItem(fim.strftime("%d/%m/%Y")))
            self.tbl_reservas.setItem(row, 4, QTableWidgetItem(status))
            self.tbl_reservas.setItem(row, 5, QTableWidgetItem(f"R$ {total:.2f}"))