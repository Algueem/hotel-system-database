import mysql.connector
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QTableWidget,
                             QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QLabel, QComboBox, QDateEdit, QMessageBox, QInputDialog,
                             QFormLayout, QGroupBox, QScrollArea, QHeaderView, QListWidget, 
                             QStackedWidget, QDialog)
from PyQt5.QtCore import QDate, QThread, pyqtSignal
from PyQt5.QtGui import QIntValidator, QDoubleValidator

class ConfigWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.schema_fields = []
        self.default_form = None
        self.bulk_forms = []
        self.is_bulk = False      
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Cabeçalho
        header = QHBoxLayout()
        btn_voltar = QPushButton("← Voltar ao Menu")
        btn_voltar.clicked.connect(self.voltar_menu)
        header.addWidget(btn_voltar)
        header.addStretch()

        # Combobox para seleção de tabela e operação
        self.cmb_tabela = QComboBox()
        self.cmb_tabela.addItems(["Funcionario", "Quarto", "Reserva", "Pagamento", "Servico", "TipoServico"])
        self.cmb_tabela.currentIndexChanged.connect(self.atualizar_interface)

        self.cmb_operacao = QComboBox()
        self.cmb_operacao.addItems(["SELECT", "INSERT", "UPDATE", "DELETE"])
        self.cmb_operacao.currentIndexChanged.connect(self.atualizar_interface)

        # Campo para condição WHERE (opcional)
        self.txt_where = QLineEdit()
        self.txt_where.setPlaceholderText("Condição WHERE (ex: id = 1)")

        # Área de quantidade e botão de gerar formulários
        self.txt_quantidade = QLineEdit()
        self.txt_quantidade.setValidator(QIntValidator(1, 100))
        self.txt_quantidade.setPlaceholderText("Quantidade de registros")
        self.btn_gerar_forms = QPushButton("Gerar Formulários")
        self.btn_gerar_forms.clicked.connect(self.gerar_formularios)

        quantidade_layout = QHBoxLayout()
        quantidade_layout.addWidget(QLabel("Quantidade a mais a ser:"))
        quantidade_layout.addWidget(self.txt_quantidade)
        quantidade_layout.addWidget(self.btn_gerar_forms)

        # Área para os formulários (usada tanto para inserção simples quanto bulk)
        self.forms_scroll = QScrollArea()
        self.forms_container = QWidget()
        self.forms_layout = QFormLayout()
        self.forms_container.setLayout(self.forms_layout)
        self.forms_scroll.setWidget(self.forms_container)
        self.forms_scroll.setWidgetResizable(True)

        # Tabela para exibir resultados de SELECT
        self.tbl_resultado = QTableWidget()

        # Montagem do layout principal
        form_top = QFormLayout()
        form_top.addRow("Tabela:", self.cmb_tabela)
        form_top.addRow("Operação:", self.cmb_operacao)

        layout.addLayout(header)
        layout.addLayout(form_top)
        layout.addLayout(quantidade_layout)
        layout.addWidget(QLabel("Campos:"))
        layout.addWidget(self.forms_scroll)
        layout.addWidget(QLabel("Condição WHERE (opcional):"))
        layout.addWidget(self.txt_where)
        btn_executar = QPushButton("Executar")
        btn_executar.clicked.connect(self.executar_query)
        layout.addWidget(btn_executar)
        layout.addWidget(self.tbl_resultado)

        self.setLayout(layout)
        self.atualizar_interface()

    def voltar_menu(self):
        self.parent().setCurrentIndex(0)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def clear_forms_layout(self):
        self.clear_layout(self.forms_layout)
        self.default_form = None
        self.bulk_forms = []
        self.is_bulk = False

    def load_schema(self):
        table = self.cmb_tabela.currentText()
        try:
            cursor = self.db.cursor()
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            self.schema_fields = []
            for col in columns:
                field_name = col[0]
                field_type = col[1]
                nullable = (col[2] == "YES")
                auto_increment = (col[5] == "auto_increment")
                if auto_increment:
                    continue
                self.schema_fields.append({
                    "name": field_name,
                    "type": field_type,
                    "nullable": nullable,
                    "auto_increment": auto_increment
                })
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar schema:\n{err}")

    def add_default_form(self):
        group_box = QGroupBox("Registro 1")
        form_layout = QFormLayout()
        fields_list = []
        for field in self.schema_fields:
            label = QLabel(f"{field['name']} ({field['type']})")
            input_field = QLineEdit()
            input_field.setPlaceholderText("Obrigatório" if not field["nullable"] else "Opcional")
            if "int" in field["type"].lower():
                input_field.setValidator(QIntValidator())
            elif "decimal" in field["type"].lower():
                input_field.setValidator(QDoubleValidator())
            form_layout.addRow(label, input_field)
            fields_list.append({
                "name": field["name"],
                "field": input_field,
                "nullable": field["nullable"],
                "type": field["type"]
            })
        group_box.setLayout(form_layout)
        self.forms_layout.addRow(group_box)
        self.default_form = fields_list

    def add_bulk_form(self, index):
        group_box = QGroupBox(f"Registro {index}")
        form_layout = QFormLayout()
        fields_list = []
        for field in self.schema_fields:
            label = QLabel(f"{field['name']} ({field['type']})")
            input_field = QLineEdit()
            input_field.setPlaceholderText("Obrigatório" if not field["nullable"] else "Opcional")
            if "int" in field["type"].lower():
                input_field.setValidator(QIntValidator())
            elif "decimal" in field["type"].lower():
                input_field.setValidator(QDoubleValidator())
            form_layout.addRow(label, input_field)
            fields_list.append({
                "name": field["name"],
                "field": input_field,
                "nullable": field["nullable"],
                "type": field["type"]
            })
        group_box.setLayout(form_layout)
        self.forms_layout.addRow(group_box)
        self.bulk_forms.append(fields_list)

    def atualizar_interface(self):
        op = self.cmb_operacao.currentText()
        if op == "INSERT":
            self.btn_gerar_forms.setEnabled(True)
            self.clear_forms_layout()
            self.load_schema()
            self.add_default_form()
            for field in self.default_form:
                field["field"].setReadOnly(False)
                field["field"].setPlaceholderText("Obrigatório" if not field["nullable"] else "Opcional")
        else:
            self.btn_gerar_forms.setEnabled(True)
            self.clear_forms_layout()
            self.load_schema()
            self.add_default_form()
            if op in ["SELECT", "DELETE"]:
                for field in self.default_form:
                    field["field"].setReadOnly(True)
            elif op == "UPDATE":
                for field in self.default_form:
                    field["field"].setReadOnly(False)
                    field["field"].setPlaceholderText("Novo valor")
        self.txt_where.setReadOnly(op not in ["SELECT", "UPDATE", "DELETE"])

    def gerar_formularios(self):
        if self.cmb_operacao.currentText() != "INSERT":
            QMessageBox.warning(self, "Aviso", "Somente para operação de inserção")
            return
        quantidade = int(self.txt_quantidade.text()) if self.txt_quantidade.text() else 1
        start_index = 2 + len(self.bulk_forms)
        for i in range(quantidade):
            self.add_bulk_form(start_index + i)
        total_forms = 1 + len(self.bulk_forms)
        self.is_bulk = (total_forms > 1)

    def validar_campos_single(self, form_fields):
        for field in form_fields:
            if not field["nullable"] and not field["field"].text():
                return f"Campo {field['name']} é obrigatório!"
        return None

    def converter_valor(self, value, field_type):
        try:
            if "int" in field_type.lower():
                return int(value)
            elif "decimal" in field_type.lower():
                return float(value)
            elif "date" in field_type.lower() or "time" in field_type.lower():
                return QDate.fromString(value, "yyyy-MM-dd").toString("yyyy-MM-dd")
            return value
        except:
            raise ValueError(f"Valor inválido para o tipo {field_type}")

    def executar_query(self):
        op = self.cmb_operacao.currentText()
        table = self.cmb_tabela.currentText()
        try:
            cursor = self.db.cursor()
            if op == "SELECT":
                where = f" WHERE {self.txt_where.text()}" if self.txt_where.text() else ""
                cursor.execute(f"SELECT * FROM {table}{where}")
                self.mostrar_resultados(cursor)
            elif op == "INSERT":
                if self.is_bulk:
                    all_values = []
                    erro = self.validar_campos_single(self.default_form)
                    if erro:
                        raise ValueError(erro)
                    valores = {}
                    for field in self.default_form:
                        if field["field"].text():
                            valores[field["name"]] = self.converter_valor(field["field"].text(), field["type"])
                    colunas = list(valores.keys())
                    all_values.append(tuple(valores[field] for field in colunas))
                    for form in self.bulk_forms:
                        erro = self.validar_campos_single(form)
                        if erro:
                            raise ValueError(erro)
                        valores_bulk = {}
                        for field in form:
                            if field["field"].text():
                                valores_bulk[field["name"]] = self.converter_valor(field["field"].text(), field["type"])
                        all_values.append(tuple(valores_bulk[field] for field in colunas))
                    placeholders = ", ".join(["%s"] * len(colunas))
                    query = f"INSERT INTO {table} ({','.join(colunas)}) VALUES ({placeholders})"
                    cursor.executemany(query, all_values)
                    self.db.commit()
                    QMessageBox.information(self, "Sucesso", f"{cursor.rowcount} registros inseridos com sucesso!")
                else:
                    erro = self.validar_campos_single(self.default_form)
                    if erro:
                        raise ValueError(erro)
                    valores = {}
                    for field in self.default_form:
                        if field["field"].text():
                            valores[field["name"]] = self.converter_valor(field["field"].text(), field["type"])
                    colunas = ", ".join(valores.keys())
                    placeholders = ", ".join(["%s"] * len(valores))
                    query = f"INSERT INTO {table} ({colunas}) VALUES ({placeholders})"
                    cursor.execute(query, list(valores.values()))
                    self.db.commit()
                    QMessageBox.information(self, "Sucesso", f"Registro inserido! ID: {cursor.lastrowid}")
            elif op == "UPDATE":
                erro = self.validar_campos_single(self.default_form)
                if erro:
                    raise ValueError(erro)
                valores = {}
                for field in self.default_form:
                    if field["field"].text():
                        valores[field["name"]] = self.converter_valor(field["field"].text(), field["type"])
                set_clause = ", ".join([f"{k} = %s" for k in valores.keys()])
                where = f" WHERE {self.txt_where.text()}" if self.txt_where.text() else ""
                query = f"UPDATE {table} SET {set_clause}{where}"
                cursor.execute(query, list(valores.values()))
                self.db.commit()
                QMessageBox.information(self, "Sucesso", f"{cursor.rowcount} registro(s) atualizado(s)!")
            elif op == "DELETE":
                where = f" WHERE {self.txt_where.text()}" if self.txt_where.text() else ""
                cursor.execute(f"DELETE FROM {table}{where}")
                self.db.commit()
                QMessageBox.information(self, "Sucesso", f"{cursor.rowcount} registro(s) excluído(s)!")
            # Após a operação, reconstrói o formulário padrão
            self.clear_forms_layout()
            self.load_schema()
            self.add_default_form()
        except Exception as err:
            self.db.rollback()
            QMessageBox.critical(self, "Erro", f"Erro na operação:\n{str(err)}")

    def mostrar_resultados(self, cursor):
        resultados = cursor.fetchall()
        self.tbl_resultado.setRowCount(len(resultados))
        self.tbl_resultado.setColumnCount(len(cursor.description))
        self.tbl_resultado.setHorizontalHeaderLabels([desc[0] for desc in cursor.description])
        for row_idx, row in enumerate(resultados):
            for col_idx, value in enumerate(row):
                self.tbl_resultado.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
