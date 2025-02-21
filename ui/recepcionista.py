import mysql.connector
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, 
                            QLineEdit, QComboBox, QDateEdit, QListWidget, QLabel, QMessageBox,
                            QGroupBox, QScrollArea, QStackedWidget)
from PyQt5.QtCore import QDate, Qt

class RecepcionistaWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_client = None
        self.initUI()
        self.setMinimumSize(1000, 700)

    def initUI(self):
        main_layout = QVBoxLayout()
        
        btn_voltar = QPushButton("← Voltar ao Menu")
        btn_voltar.clicked.connect(lambda: self.parent().setCurrentIndex(0))
        main_layout.addWidget(btn_voltar)

        self.stacked_widget = QStackedWidget()
        
        self.page_recepcionista = self.criar_pagina_recepcionista()
        self.stacked_widget.addWidget(self.page_recepcionista)

        self.page_cliente = self.criar_pagina_cliente()
        self.stacked_widget.addWidget(self.page_cliente)

        self.page_reserva = self.criar_pagina_reserva()
        self.stacked_widget.addWidget(self.page_reserva)

        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
        self.carregar_recepcionistas()

    def criar_pagina_recepcionista(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Identificação do Recepcionista")
        form = QFormLayout()
        
        self.cmb_recepcionistas = QComboBox()
        form.addRow("Recepcionista:", self.cmb_recepcionistas)
        
        btn_proximo = QPushButton("Próximo →")
        btn_proximo.clicked.connect(self.ir_para_cliente)
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addWidget(btn_proximo, alignment=Qt.AlignRight)
        page.setLayout(layout)
        return page

    def criar_pagina_cliente(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Grupo de busca de cliente
        group_busca = QGroupBox("Buscar Cliente")
        form_busca = QFormLayout()
        self.txt_cpf_busca = QLineEdit()
        self.txt_cpf_busca.setInputMask("999.999.999-99")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_cliente)
        form_busca.addRow("CPF:", self.txt_cpf_busca)
        form_busca.addRow(btn_buscar)
        group_busca.setLayout(form_busca)

        # Grupo de cadastro de cliente
        self.group_cadastro = QGroupBox("Cadastrar Novo Cliente")
        form_cadastro = QFormLayout()
        self.txt_nome = QLineEdit()
        self.txt_telefone = QLineEdit()
        self.txt_email = QLineEdit()
        form_cadastro.addRow("Nome*:", self.txt_nome)
        form_cadastro.addRow("Telefone:", self.txt_telefone)
        form_cadastro.addRow("Email:", self.txt_email)
        btn_cadastrar = QPushButton("Cadastrar e Continuar")
        btn_cadastrar.clicked.connect(self.cadastrar_cliente)
        form_cadastro.addRow(btn_cadastrar)
        self.group_cadastro.hide()
        self.group_cadastro.setLayout(form_cadastro)

        layout.addWidget(group_busca)
        layout.addWidget(self.group_cadastro)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def criar_pagina_reserva(self):
        page = QWidget()
        layout = QVBoxLayout()
        
        # Grupo de reserva
        group_reserva = QGroupBox("Detalhes da Reserva")
        form_reserva = QFormLayout()
        
        self.cmb_quarto = QComboBox()
        self.date_inicio = QDateEdit(QDate.currentDate())
        self.date_fim = QDateEdit(QDate.currentDate().addDays(1))
        self.cmb_servicos = QComboBox()
        self.lista_servicos = QListWidget()
        self.servicos_selecionados = []
        
        btn_add_servico = QPushButton("Adicionar Serviço →")
        btn_add_servico.clicked.connect(self.adicionar_servico)
        
        # Grupo de pagamento
        self.group_pagamento = QGroupBox("Pagamento")
        pagamento_layout = QFormLayout()
        self.cmb_metodo = QComboBox()
        self.cmb_metodo.addItems(["Crédito", "Débito", "Dinheiro"])
        pagamento_layout.addRow("Método:", self.cmb_metodo)
        self.group_pagamento.setLayout(pagamento_layout)

        form_reserva.addRow("Quarto:", self.cmb_quarto)
        form_reserva.addRow("Data Início:", self.date_inicio)
        form_reserva.addRow("Data Fim:", self.date_fim)
        form_reserva.addRow("Serviços:", self.cmb_servicos)
        form_reserva.addRow(btn_add_servico)
        form_reserva.addRow("Serviços Selecionados:", self.lista_servicos)
        form_reserva.addRow(self.group_pagamento)
        
        btn_finalizar = QPushButton("Finalizar Reserva")
        btn_finalizar.clicked.connect(self.finalizar_reserva)
        
        group_reserva.setLayout(form_reserva)
        layout.addWidget(group_reserva)
        layout.addWidget(btn_finalizar)
        page.setLayout(layout)
        return page

    def carregar_recepcionistas(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT f.idFuncionario, f.Nome 
                FROM Funcionario f
                JOIN Recepcionista r ON f.idFuncionario = r.idFuncionario
            """)
            self.cmb_recepcionistas.clear()
            for id_func, nome in cursor:
                self.cmb_recepcionistas.addItem(f"{nome} (ID: {id_func})", id_func)
                
            if self.cmb_recepcionistas.count() == 0:
                QMessageBox.warning(self, "Aviso", "Nenhum recepcionista cadastrado!")
                
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar recepcionistas:\n{err}")

    def buscar_cliente(self):
        cpf = self.txt_cpf_busca.text().replace(".", "").replace("-", "")
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM Cliente WHERE CPF = %s", (cpf,))
            cliente = cursor.fetchone()
            
            if cliente:
                self.current_client = cliente
                QMessageBox.information(self, "Cliente Encontrado", 
                    f"Nome: {cliente[1]}\nTelefone: {cliente[2]}\nEmail: {cliente[3]}")
                self.ir_para_reserva()
            else:
                self.group_cadastro.show()
                self.txt_nome.setFocus()
                
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro na busca:\n{err}")

    def cadastrar_cliente(self):
        if not self.txt_nome.text():
            QMessageBox.warning(self, "Aviso", "Nome é obrigatório!")
            return
            
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO Cliente (CPF, Nome, Telefone, Email)
                VALUES (%s, %s, %s, %s)
            """, (
                self.txt_cpf_busca.text().replace(".", "").replace("-", ""),
                self.txt_nome.text(),
                self.txt_telefone.text() or None,
                self.txt_email.text() or None
            ))
            self.db.commit()
            self.current_client = cursor.lastrowid
            self.ir_para_reserva()
            
        except mysql.connector.Error as err:
            self.db.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao cadastrar:\n{err}")

    def ir_para_cliente(self):
        if self.cmb_recepcionistas.currentIndex() == -1:
            QMessageBox.warning(self, "Aviso", "Selecione um recepcionista!")
            return
        self.stacked_widget.setCurrentIndex(1)

    def carregar_dados(self):
        self.carregar_servicos()
        self.carregar_quartos()
        self.carregar_recepcionistas()

    def ir_para_reserva(self):
        self.carregar_quartos()
        self.carregar_servicos()
        self.stacked_widget.setCurrentIndex(2)

    def carregar_quartos(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT 1 FROM Quarto WHERE EXISTS (SELECT 1 FROM Quarto WHERE status = 'Disponível')")
            if cursor.fetchall():
                cursor.execute("SELECT numero_quarto FROM Quarto WHERE status = 'Disponível'")
                self.cmb_quarto.clear()
                for (quarto,) in cursor:
                    self.cmb_quarto.addItem(str(quarto))
            else:
                QMessageBox.warning(self, "Aviso", "Não há quartos disponíveis!")
                return
            
            
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar quartos:\n{err}")

    def carregar_servicos(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT tipo, valor FROM TipoServico")
            self.cmb_servicos.clear()
            for tipo, valor in cursor:
                self.cmb_servicos.addItem(f"{tipo} (R$ {valor:.2f})", tipo)
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar serviços:\n{err}")

    def adicionar_servico(self):
        servico = self.cmb_servicos.currentData()
        if servico and servico not in self.servicos_selecionados:
            self.servicos_selecionados.append(servico)
            self.lista_servicos.addItem(self.cmb_servicos.currentText())

    def finalizar_reserva(self):
        try:
            cursor = self.db.cursor()
            
            # Inserir Reserva
            cursor.execute("""
                INSERT INTO Reserva (
                    CPF_cliente, 
                    data_inicio, 
                    data_fim, 
                    idRecepcionista, 
                    idQuarto
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                self.txt_cpf_busca.text().replace(".", "").replace("-", ""),
                self.date_inicio.date().toString("yyyy-MM-dd"),
                self.date_fim.date().toString("yyyy-MM-dd"),
                self.cmb_recepcionistas.currentData(),
                int(self.cmb_quarto.currentText())
            ))
            reserva_id = cursor.lastrowid
            
            # Calcular valor total
            cursor.execute("""
                SELECT SUM(ts.valor) 
                FROM TipoServico ts 
                WHERE ts.tipo IN ({})
            """.format(",".join(["%s"]*len(self.servicos_selecionados))), 
            self.servicos_selecionados)
            valor_servicos = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT preco FROM Quarto WHERE numero_quarto = %s", 
                          (int(self.cmb_quarto.currentText()),))
            valor_quarto = cursor.fetchone()[0]
            total = valor_quarto + valor_servicos
            
            # Inserir Pagamento
            cursor.execute("""
                INSERT INTO Pagamento (
                    metodo, 
                    valor, 
                    idReserva
                ) VALUES (%s, %s, %s)
            """, (
                self.cmb_metodo.currentText(),
                total,
                reserva_id
            ))
            
            # Inserir Serviços
            if self.servicos_selecionados:
                cursor.executemany(
                    "INSERT INTO Servico (idReserva, tipoServico) VALUES (%s, %s)",
                    [(reserva_id, servico) for servico in self.servicos_selecionados]
                )

            
            # Atualizar status do quarto
            cursor.execute("""
                UPDATE Quarto 
                SET status = 'Ocupado' 
                WHERE numero_quarto = %s
            """, (int(self.cmb_quarto.currentText()),))
            
            self.db.commit()
            QMessageBox.information(self, "Sucesso", "Reserva finalizada com sucesso!")
            self.reset_form()
            
        except mysql.connector.Error as err:
            self.db.rollback()
            QMessageBox.critical(self, "Erro", f"Erro na reserva:\n{err}")

    def reset_form(self):
        self.stacked_widget.setCurrentIndex(0)
        self.txt_cpf_busca.clear()
        self.txt_nome.clear()
        self.txt_telefone.clear()
        self.txt_email.clear()
        self.group_cadastro.hide()
        self.lista_servicos.clear()
        self.servicos_selecionados = []
        self.carregar_recepcionistas()
