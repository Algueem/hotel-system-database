import mysql.connector
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QTableWidget,
                             QTableWidgetItem, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QLabel, QComboBox, QDateEdit, QMessageBox, QInputDialog,
                             QFormLayout, QGroupBox, QScrollArea, QHeaderView, QListWidget, 
                             QStackedWidget, QDialog, QListWidgetItem, QRadioButton, QButtonGroup)
from PyQt5.QtCore import QDate, QThread, pyqtSignal
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from collections import defaultdict

class GerenteWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.setMinimumSize(1200, 800)
        self.quartos = defaultdict(dict)

    def initUI(self):
        layout = QVBoxLayout()
        
        header = QHBoxLayout()
        btn_voltar = QPushButton("← Voltar ao Menu")
        btn_voltar.clicked.connect(self.voltar_menu)
        header.addWidget(btn_voltar)
        header.addStretch()

        tabs = QTabWidget()
        
        # Aba Quartos – consulta com LEFT JOIN para trazer a camareira atribuída
        tab_quartos = QWidget()
        self.layout_quartos = QVBoxLayout()
        
        header_quartos = QHBoxLayout()
        btn_novo_quarto = QPushButton("Novo Quarto")
        btn_novo_quarto.clicked.connect(self.criar_novo_quarto)
        header_quartos.addWidget(btn_novo_quarto)
        header_quartos.addStretch()
        
        self.scroll_quartos = QScrollArea()
        self.quartos_container = QWidget()
        self.quartos_layout = QVBoxLayout()
        self.quartos_container.setLayout(self.quartos_layout)
        self.scroll_quartos.setWidget(self.quartos_container)
        self.scroll_quartos.setWidgetResizable(True)
        
        self.layout_quartos.addLayout(header_quartos)
        self.layout_quartos.addWidget(self.scroll_quartos)
        tab_quartos.setLayout(self.layout_quartos)
        
        # Aba Funcionários – com sub-abas
        tab_func = QWidget()
        self.layout_func = QVBoxLayout()
        
        # Cabeçalho da aba Funcionários
        header_func = QHBoxLayout()
        btn_novo_func = QPushButton("Novo Funcionário")
        btn_novo_func.clicked.connect(self.criar_novo_funcionario)
        header_func.addWidget(btn_novo_func)
        header_func.addStretch()
        
        # Abas internas de Funcionários
        self.tabs_func = QTabWidget()
        
        # Aba Recepcionistas
        self.tab_recepcionistas = QWidget()
        layout_recepcionistas = QHBoxLayout()
        self.lista_recepcionistas = QListWidget()
        self.lista_recepcionistas.itemSelectionChanged.connect(self.mostrar_detalhes_recepcionista)
        self.detalhes_recepcionista = QFormLayout()
        layout_recepcionistas.addWidget(self.lista_recepcionistas, 30)
        layout_recepcionista_container = QWidget()
        layout_recepcionista_container.setLayout(self.detalhes_recepcionista)
        layout_recepcionistas.addWidget(layout_recepcionista_container, 70)
        self.tab_recepcionistas.setLayout(layout_recepcionistas)
        self.tabs_func.addTab(self.tab_recepcionistas, "Recepcionistas")
        
        # Aba Camareiras
        self.tab_camareiras = QWidget()
        layout_camareiras = QHBoxLayout()
        self.lista_camareiras = QListWidget()
        self.lista_camareiras.itemSelectionChanged.connect(self.mostrar_detalhes_camareira)
        self.detalhes_camareira = QFormLayout()
        layout_camareiras.addWidget(self.lista_camareiras, 30)
        layout_camareiras_container = QWidget()
        layout_camareiras_container.setLayout(self.detalhes_camareira)
        layout_camareiras.addWidget(layout_camareiras_container, 70)
        self.tab_camareiras.setLayout(layout_camareiras)
        self.tabs_func.addTab(self.tab_camareiras, "Camareiras")
        
        # Aba Pesquisa Funcionários – com filtros e ordenação
        self.tab_pesquisa = QWidget()
        layout_pesquisa = QVBoxLayout()
        
        # Linha de filtros
        filter_layout = QHBoxLayout()
        self.rbtn_todos = QRadioButton("Todos")
        self.rbtn_recepcionista = QRadioButton("Recepcionista")
        self.rbtn_camareira = QRadioButton("Camareira")
        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.rbtn_todos)
        self.btn_group.addButton(self.rbtn_recepcionista)
        self.btn_group.addButton(self.rbtn_camareira)
        self.rbtn_todos.setChecked(True)
        filter_layout.addWidget(QLabel("Filtrar por:"))
        filter_layout.addWidget(self.rbtn_todos)
        filter_layout.addWidget(self.rbtn_recepcionista)
        filter_layout.addWidget(self.rbtn_camareira)
        
        # Caixa para busca por quantidade de reservas (habilitada somente para recepcionista)
        self.txt_reservas = QLineEdit()
        self.txt_reservas.setPlaceholderText("Quantidade de reservas")
        self.txt_reservas.setEnabled(False)
        filter_layout.addWidget(QLabel("Reservas:"))
        filter_layout.addWidget(self.txt_reservas)
        
        # Botão toggle para ordenação
        self.btn_toggle_ordem = QPushButton("Vendas Crescente")
        filter_layout.addWidget(self.btn_toggle_ordem)
        
        # Conexões: habilitar caixa de reservas somente se recepcionista estiver selecionado
        self.rbtn_recepcionista.toggled.connect(lambda checked: self.txt_reservas.setEnabled(checked))
        self.btn_toggle_ordem.clicked.connect(self.toggle_ordem)
        
        layout_pesquisa.addLayout(filter_layout)
        
        # Linha de busca por nome
        search_layout = QHBoxLayout()
        self.txt_pesquisa_func = QLineEdit()
        self.txt_pesquisa_func.setPlaceholderText("Digite parte do nome do funcionário")
        btn_pesquisar = QPushButton("Pesquisar")
        btn_pesquisar.clicked.connect(self.pesquisar_funcionarios)
        search_layout.addWidget(self.txt_pesquisa_func)
        search_layout.addWidget(btn_pesquisar)
        layout_pesquisa.addLayout(search_layout)
        
        self.tbl_pesquisa_func = QTableWidget()
        self.tbl_pesquisa_func.setColumnCount(5)
        self.tbl_pesquisa_func.setHorizontalHeaderLabels(["ID", "Nome", "Salário", "Categoria", "Reservas"])
        self.tbl_pesquisa_func.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout_pesquisa.addWidget(self.tbl_pesquisa_func)
        
        self.tab_pesquisa.setLayout(layout_pesquisa)
        self.tabs_func.addTab(self.tab_pesquisa, "Pesquisa Funcionários")
        
        self.layout_func.addLayout(header_func)
        self.layout_func.addWidget(self.tabs_func)
        tab_func.setLayout(self.layout_func)
        
        tabs.addTab(tab_quartos, "Quartos")
        tabs.addTab(tab_func, "Funcionários")
        layout.addLayout(header)
        layout.addWidget(tabs)
        
        self.setLayout(layout)

    def voltar_menu(self):
        self.parent().setCurrentIndex(0)

    def carregar_dados(self):
        self.carregar_quartos()
        self.carregar_funcionarios()

    # ========== MÉTODOS PARA QUARTOS ==========
    def carregar_quartos(self):
        while self.quartos_layout.count():
            widget = self.quartos_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()
        self.quartos.clear()
        try:
            cursor = self.db.cursor()
            query = """
                SELECT q.numero_quarto, q.numero_camas, q.adicionais, q.status, q.preco, c.idFuncionario
                FROM Quarto q
                LEFT JOIN Camareira c ON q.numero_quarto = c.idQuarto
                ORDER BY q.numero_quarto
            """
            cursor.execute(query)
            for quarto in cursor:
                self.criar_card_quarto(quarto)
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar quartos:\n{err}")

    def criar_card_quarto(self, quarto):
        numero, camas, adicionais, status, preco, camareira_id = quarto
        card = QGroupBox(f"Quarto {numero}")
        layout = QFormLayout()
        
        self.quartos[numero]['txt_numero'] = QLineEdit(str(numero))
        self.quartos[numero]['txt_numero'].setReadOnly(True)
        self.quartos[numero]['txt_camas'] = QLineEdit(str(camas))
        self.quartos[numero]['txt_adicionais'] = QLineEdit(adicionais)
        self.quartos[numero]['txt_preco'] = QLineEdit(str(preco))
        self.quartos[numero]['cmb_status'] = QComboBox()
        self.quartos[numero]['cmb_status'].addItems(["Disponível", "Ocupado", "Manutenção"])
        self.quartos[numero]['cmb_status'].setCurrentText(status)
        
        lbl_camareira = QLabel(str(camareira_id) if camareira_id is not None else "Nenhuma")
        
        btn_salvar = QPushButton("Salvar")
        btn_salvar.clicked.connect(lambda: self.salvar_quarto(numero))
        btn_excluir = QPushButton("Excluir")
        btn_excluir.clicked.connect(lambda: self.excluir_quarto(numero))
        
        layout.addRow("Número:", self.quartos[numero]['txt_numero'])
        layout.addRow("Camas:", self.quartos[numero]['txt_camas'])
        layout.addRow("Preço:", self.quartos[numero]['txt_preco'])
        layout.addRow("Adicionais:", self.quartos[numero]['txt_adicionais'])
        layout.addRow("Status:", self.quartos[numero]['cmb_status'])
        layout.addRow("Camareira Atribuída:", lbl_camareira)
        layout.addRow(btn_salvar)
        layout.addRow(btn_excluir)
        
        card.setLayout(layout)
        self.quartos_layout.addWidget(card)

    def criar_novo_quarto(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo Quarto")
        layout = QFormLayout()
        
        txt_numero = QLineEdit()
        txt_camas = QLineEdit()
        txt_adicionais = QLineEdit()
        txt_preco = QLineEdit()
        cmb_status = QComboBox()
        cmb_status.addItems(["Disponível", "Ocupado", "Manutenção"])
        
        btn_salvar = QPushButton("Criar")
        btn_salvar.clicked.connect(lambda: self.salvar_novo_quarto(
            txt_numero.text(),
            txt_camas.text(),
            txt_adicionais.text(),
            cmb_status.currentText(),
            txt_preco.text(),
            dialog
        ))
        
        layout.addRow("Número:", txt_numero)
        layout.addRow("Camas:", txt_camas)
        layout.addRow("Adicionais:", txt_adicionais)
        layout.addRow("Preço:", txt_preco)
        layout.addRow("Status:", cmb_status)
        layout.addRow(btn_salvar)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def salvar_novo_quarto(self, numero, camas, adicionais, status, preco, dialog):
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO Quarto (numero_quarto, numero_camas, adicionais, status, preco)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (numero, camas, adicionais, status, preco)
            cursor.execute(query, values)
            self.db.commit()
            self.carregar_quartos()
            dialog.close()
            self.carregar_funcionarios()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao criar quarto:\n{err}")

    def salvar_quarto(self, numero):
        camas = self.quartos[numero]['txt_camas'].text()
        adicionais = self.quartos[numero]['txt_adicionais'].text()
        status = self.quartos[numero]['cmb_status'].currentText()
        preco = self.quartos[numero]['txt_preco'].text()
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE Quarto SET
                    numero_camas = %s,
                    adicionais = %s,
                    status = %s,
                    preco = %s
                WHERE numero_quarto = %s
            """, (camas, adicionais, status, preco, numero))
            self.db.commit()
            self.carregar_quartos()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar quarto:\n{err}")

    def excluir_quarto(self, numero):
        confirm = QMessageBox.question(
            self, "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o quarto {numero}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                cursor = self.db.cursor()
                cursor.execute("DELETE FROM Quarto WHERE numero_quarto = %s", (numero,))
                self.db.commit()
                self.carregar_quartos()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir quarto:\n{err}")

    # ========== MÉTODOS PARA FUNCIONÁRIOS ==========
    def carregar_funcionarios(self):
        self.lista_recepcionistas.clear()
        self.lista_camareiras.clear()
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT f.idFuncionario, f.Nome 
                FROM Funcionario f
                JOIN Recepcionista r ON f.idFuncionario = r.idFuncionario
                GROUP BY f.idFuncionario
            """)
            for id_func, nome in cursor:
                self.lista_recepcionistas.addItem(f"{id_func} - {nome}")
            
            cursor.execute("""
                SELECT f.idFuncionario, f.Nome 
                FROM Funcionario f
                JOIN Camareira c ON f.idFuncionario = c.idFuncionario
                GROUP BY f.idFuncionario
            """)
            for id_func, nome in cursor:
                self.lista_camareiras.addItem(f"{id_func} - {nome}")
                
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar funcionários:\n{err}")

    def criar_novo_funcionario(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Novo Funcionário")
        layout = QFormLayout()
        
        txt_nome = QLineEdit()
        txt_salario = QLineEdit()
        txt_salario.setValidator(QDoubleValidator())
        txt_telefone = QLineEdit()
        txt_email = QLineEdit()
        cmb_cargo = QComboBox()
        cmb_cargo.addItems(["Recepcionista", "Camareira"])
        txt_horario_ou_quarto = QLineEdit()
        
        def update_form():
            if cmb_cargo.currentText() == "Camareira":
                layout.itemAt(8).widget().setText("Quarto*:")
                txt_horario_ou_quarto.setValidator(QIntValidator())
            else:
                layout.itemAt(8).widget().setText("Horário*:")
                txt_horario_ou_quarto.setValidator(None)
            
        cmb_cargo.currentIndexChanged.connect(update_form)
        
        btn_salvar = QPushButton("Criar")
        btn_salvar.clicked.connect(lambda: self.salvar_novo_funcionario(
            txt_nome.text(),
            txt_salario.text(),
            txt_telefone.text(),
            txt_email.text(),
            cmb_cargo.currentText(),
            txt_horario_ou_quarto.text(),
            dialog
        ))
        
        layout.addRow("Nome*:", txt_nome)
        layout.addRow("Salário*:", txt_salario)
        layout.addRow("Telefone:", txt_telefone)
        layout.addRow("Email:", txt_email)
        layout.addRow(QLabel("Horário*:"), txt_horario_ou_quarto)
        layout.addRow("Cargo*:", cmb_cargo)
        layout.addRow(btn_salvar)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def salvar_novo_funcionario(self, nome, salario, telefone, email, cargo, horario_ou_quarto, dialog):
        if not nome or not salario or not horario_ou_quarto:
            QMessageBox.warning(self, "Aviso", "Campos obrigatórios faltando!")
            return
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO Funcionario (Nome, Salario, Telefone, Email)
                VALUES (%s, %s, %s, %s)
            """, (nome, salario, telefone or None, email or None))
            id_func = cursor.lastrowid
            
            if cargo == "Recepcionista":
                cursor.execute("""
                    INSERT INTO Recepcionista (idFuncionario, HorarioAtendimento)
                    VALUES (%s, %s)
                """, (id_func, horario_ou_quarto))
            else:
                cursor.execute("SELECT numero_quarto FROM Quarto WHERE numero_quarto = %s", (horario_ou_quarto,))
                if not cursor.fetchone():
                    QMessageBox.warning(self, "Erro", "Quarto não encontrado!")
                    self.db.rollback()
                    return
                
                cursor.execute("SELECT idFuncionario FROM Camareira WHERE idQuarto = %s", (horario_ou_quarto,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Erro", "Quarto já tem uma camareira!")
                    self.db.rollback()
                    return
                
                cursor.execute("""
                    INSERT INTO Camareira (idFuncionario, idQuarto)
                    VALUES (%s, %s)
                """, (id_func, horario_ou_quarto))
            
            self.db.commit()
            self.carregar_funcionarios()
            dialog.close()
        except mysql.connector.Error as err:
            self.db.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao criar funcionário:\n{err}")

    def mostrar_detalhes_recepcionista(self):
        while self.detalhes_recepcionista.count():
            item = self.detalhes_recepcionista.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        selected = self.lista_recepcionistas.currentItem()
        if not selected:
            return
            
        id_func = int(selected.text().split(" - ")[0])
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT f.Nome, f.Salario, r.HorarioAtendimento, r.ReservasRealizadas
                FROM Funcionario f
                JOIN Recepcionista r ON f.idFuncionario = r.idFuncionario
                WHERE f.idFuncionario = %s
            """, (id_func,))
            r = cursor.fetchone()
            if not r:
                return
            nome, salario, horario, reservas = r
            
            self.txt_salario = QLineEdit(str(salario))
            self.txt_horario = QLineEdit(horario)
            
            self.detalhes_recepcionista.addRow(QLabel("Nome:"), QLabel(nome))
            self.detalhes_recepcionista.addRow(QLabel("Salário:"), self.txt_salario)
            self.detalhes_recepcionista.addRow(QLabel("Horário:"), self.txt_horario)
            self.detalhes_recepcionista.addRow(QLabel("Reservas Realizadas:"), QLabel(str(reservas)))
            
            btn_salvar = QPushButton("Salvar Alterações")
            btn_salvar.clicked.connect(lambda: self.salvar_alteracoes_recepcionista(id_func))
            self.detalhes_recepcionista.addRow(btn_salvar)
            
            btn_excluir = QPushButton("Excluir Funcionário")
            btn_excluir.clicked.connect(lambda: self.excluir_funcionario(id_func, "Recepcionista"))
            self.detalhes_recepcionista.addRow(btn_excluir)
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar detalhes:\n{err}")

    def salvar_alteracoes_recepcionista(self, id_func):
        novo_salario = self.txt_salario.text()
        novo_horario = self.txt_horario.text()
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE Funcionario 
                SET Salario = %s 
                WHERE idFuncionario = %s
            """, (novo_salario, id_func))
            
            cursor.execute("""
                UPDATE Recepcionista 
                SET HorarioAtendimento = %s 
                WHERE idFuncionario = %s
            """, (novo_horario, id_func))
            
            self.db.commit()
            QMessageBox.information(self, "Sucesso", "Alterações salvas com sucesso!")
            self.carregar_funcionarios()
        except mysql.connector.Error as err:
            self.db.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao salvar alterações:\n{err}")

    def mostrar_detalhes_camareira(self):
        while self.detalhes_camareira.count():
            item = self.detalhes_camareira.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        selected = self.lista_camareiras.currentItem()
        if not selected:
            return

        id_func = int(selected.text().split(" - ")[0])

        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT f.Nome, f.Salario, GROUP_CONCAT(c.idQuarto)
                FROM Funcionario f
                LEFT JOIN Camareira c ON f.idFuncionario = c.idFuncionario
                WHERE f.idFuncionario = %s
                GROUP BY f.idFuncionario
            """, (id_func,))
            r = cursor.fetchone()
            if not r:
                return
            nome, salario, quartos = r

            self.txt_salario_camareira = QLineEdit(str(salario))

            self.detalhes_camareira.addRow(QLabel("Nome:"), QLabel(nome))
            self.detalhes_camareira.addRow(QLabel("Salário:"), self.txt_salario_camareira)

            lbl_quartos = QLabel("Quartos Atribuídos:")
            self.lista_quartos_atribuidos = QListWidget()

            if quartos:
                for q in quartos.split(','):
                    item = QListWidgetItem(q)
                    item.setData(32, q)
                    self.lista_quartos_atribuidos.addItem(item)

            btn_remover_quarto = QPushButton("Remover Quarto Selecionado")
            btn_remover_quarto.clicked.connect(lambda: self.desatribuir_quarto(id_func))

            self.detalhes_camareira.addRow(lbl_quartos)
            self.detalhes_camareira.addRow(self.lista_quartos_atribuidos)
            self.detalhes_camareira.addRow(btn_remover_quarto)

            cmb_quartos = QComboBox()
            cursor.execute("SELECT numero_quarto FROM Quarto")
            cmb_quartos.addItems([str(q[0]) for q in cursor])

            btn_adicionar = QPushButton("Atribuir Novo Quarto")
            btn_adicionar.clicked.connect(lambda: self.atribuir_quarto(id_func, cmb_quartos.currentText()))
            self.detalhes_camareira.addRow(QLabel("Atribuir Novo Quarto:"), cmb_quartos)
            self.detalhes_camareira.addRow(btn_adicionar)

            btn_salvar = QPushButton("Salvar Alterações")
            btn_salvar.clicked.connect(lambda: self.salvar_alteracoes_camareira(id_func))
            self.detalhes_camareira.addRow(btn_salvar)

            btn_excluir = QPushButton("Excluir Funcionário")
            btn_excluir.clicked.connect(lambda: self.excluir_funcionario(id_func, "Camareira"))
            self.detalhes_camareira.addRow(btn_excluir)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar detalhes:\n{err}")

    def desatribuir_quarto(self, id_func):
        selected = self.lista_quartos_atribuidos.currentItem()
        if not selected:
            QMessageBox.warning(self, "Aviso", "Selecione um quarto para remover!")
            return

        numero_quarto = selected.data(32)
        confirm = QMessageBox.question(
            self, "Confirmar Remoção",
            f"Tem certeza que deseja remover o quarto {numero_quarto} desta camareira?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    DELETE FROM Camareira 
                    WHERE idFuncionario = %s 
                    AND idQuarto = %s
                """, (id_func, numero_quarto))
                self.db.commit()
                self.mostrar_detalhes_camareira()
                QMessageBox.information(self, "Sucesso", "Quarto desatribuído com sucesso!")
            except mysql.connector.Error as err:
                self.db.rollback()
                QMessageBox.critical(self, "Erro", f"Erro ao desatribuir quarto:\n{err}")

    def salvar_alteracoes_camareira(self, id_func):
        novo_salario = self.txt_salario_camareira.text()
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE Funcionario 
                SET Salario = %s 
                WHERE idFuncionario = %s
            """, (novo_salario, id_func))
            self.db.commit()
            QMessageBox.information(self, "Sucesso", "Alterações salvas com sucesso!")
            self.carregar_funcionarios()
        except mysql.connector.Error as err:
            self.db.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao salvar alterações:\n{err}")

    def atribuir_quarto(self, id_func, numero_quarto):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT idFuncionario FROM Camareira WHERE idQuarto = %s", (numero_quarto,))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("""
                    UPDATE Camareira 
                    SET idFuncionario = %s 
                    WHERE idQuarto = %s
                """, (id_func, numero_quarto))
            else:
                cursor.execute("""
                    INSERT INTO Camareira (idFuncionario, idQuarto)
                    VALUES (%s, %s)
                """, (id_func, numero_quarto))
            self.db.commit()
            self.mostrar_detalhes_camareira()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao atribuir quarto:\n{err}")

    def excluir_funcionario(self, id_func, type_func):
        confirm = QMessageBox.question(
            self, "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o funcionário {id_func}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                cursor = self.db.cursor()
                if type_func == "Recepcionista":
                    cursor.execute("DELETE FROM Recepcionista WHERE idFuncionario = %s", (id_func,))
                else:
                    cursor.execute("DELETE FROM Camareira WHERE idFuncionario = %s", (id_func,))
                cursor.execute("DELETE FROM Funcionario WHERE idFuncionario = %s", (id_func,))
                self.db.commit()
                self.carregar_funcionarios()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir funcionário:\n{err}")

    # ========== MÉTODO PARA PESQUISA DE FUNCIONÁRIOS ==========
    def pesquisar_funcionarios(self):
        nome_pattern = f"%{self.txt_pesquisa_func.text().strip()}%" if self.txt_pesquisa_func.text().strip() else "%"
        selected_filter = "Todos"
        if self.rbtn_recepcionista.isChecked():
            selected_filter = "Recepcionista"
        elif self.rbtn_camareira.isChecked():
            selected_filter = "Camareira"
        
        ordem = "ASC"
        if self.btn_toggle_ordem.text().strip() == "Vendas Decrescente":
            ordem = "DESC"
        
        try:
            cursor = self.db.cursor()
            if selected_filter == "Recepcionista":
                query = """
                    SELECT f.idFuncionario, f.Nome, f.Salario, 'Recepcionista' AS Categoria, COUNT(r.idReserva) as 'Quantidade de Reservas'
                    FROM Reserva r 
                    JOIN Funcionario f ON f.idFuncionario = r.idRecepcionista 
                    WHERE LOWER(f.Nome) LIKE LOWER(%s)
                    GROUP BY f.idFuncionario
                    HAVING COUNT(r.idReserva) > %s
                    ORDER BY COUNT(r.idReserva) """ + ordem
                params = [nome_pattern]
                params.append(self.txt_reservas.text().strip() or "0")
                cursor.execute(query, tuple(params))
            elif selected_filter == "Camareira":
                query = "SELECT f.idFuncionario, f.Nome, f.Salario, 'Camareira' AS Categoria, NULL as 'Quantidade de Reservas' FROM Funcionario f JOIN Camareira c ON f.idFuncionario = c.idFuncionario WHERE f.Nome LIKE %s ORDER BY f.Nome"
                cursor.execute(query, (nome_pattern,))
            else:  # Todos
                query = """
                (SELECT f.idFuncionario, f.Nome, f.Salario, 'Recepcionista' AS Categoria, NULL as 'Quantidade de Reservas'
                 FROM Funcionario f
                 JOIN Recepcionista r ON f.idFuncionario = r.idFuncionario
                 WHERE LOWER(f.Nome) LIKE LOWER(%s))
                UNION
                (SELECT f.idFuncionario, f.Nome, f.Salario, 'Camareira' AS Categoria, NULL as 'Quantidade de Reservas'
                 FROM Funcionario f
                 JOIN Camareira c ON f.idFuncionario = c.idFuncionario
                 WHERE LOWER(f.Nome) LIKE LOWER(%s))
                ORDER BY Nome
                """
                cursor.execute(query, (nome_pattern, nome_pattern))
            
            resultados = cursor.fetchall()
            self.tbl_pesquisa_func.setRowCount(len(resultados))
            for row_idx, row in enumerate(resultados):
                for col_idx, value in enumerate(row):
                    self.tbl_pesquisa_func.setItem(row_idx, col_idx, QTableWidgetItem(str(value) if value is not None else ""))
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro na pesquisa:\n{err}")

    def toggle_ordem(self):
        current_text = self.btn_toggle_ordem.text()
        if current_text == "Vendas Crescente":
            self.btn_toggle_ordem.setText("Vendas Decrescente")
        else:
            self.btn_toggle_ordem.setText("Vendas Crescente")
