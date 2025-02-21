-- Criação do Banco de Dados
CREATE DATABASE IF NOT EXISTS hotel_db;
USE hotel_db;

-- Tabela Funcionario
CREATE TABLE Funcionario (
    idFuncionario INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(100) NOT NULL,
    Salario DECIMAL(10,2) NOT NULL,
    Telefone VARCHAR(15),
    Email VARCHAR(100)
);

-- Tabela Recepcionista (1:1 com Funcionario)
CREATE TABLE Recepcionista (
    idFuncionario INT PRIMARY KEY,
    HorarioAtendimento VARCHAR(50) NOT NULL,
    ReservasRealizadas INT DEFAULT 0,
    FOREIGN KEY (idFuncionario) REFERENCES Funcionario(idFuncionario)
);

-- Tabela Quarto
CREATE TABLE Quarto (
    numero_quarto INT PRIMARY KEY,
    numero_camas INT NOT NULL,
    adicionais VARCHAR(255) DEFAULT 'Nenhum',
    status ENUM('Disponível', 'Ocupado', 'Manutenção') DEFAULT 'Disponível'
    valor DECIMAL(10,2) NOT NULL,
);

-- Tabela Camareira 
CREATE TABLE Camareira (
    idFuncionario INT,
    idQuarto INT,
    PRIMARY KEY (idFuncionario, idQuarto),
    FOREIGN KEY (idFuncionario) REFERENCES Funcionario(idFuncionario),
    FOREIGN KEY (idQuarto) REFERENCES Quarto(numero_quarto)
);

-- Tabela Pagamento 
CREATE TABLE Pagamento (
    idPagamento INT PRIMARY KEY AUTO_INCREMENT,
    metodo ENUM('Crédito', 'Débito', 'Dinheiro') NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    idReserva INT UNIQUE,
    FOREIGN KEY (idReserva) REFERENCES Reserva(idReserva)
);

-- Tabela TipoServico
CREATE TABLE TipoServico (
    tipo VARCHAR(50) PRIMARY KEY,
    descricao TEXT NOT NULL,
    valor DECIMAL(10,2) NOT NULL
);

-- Tabela Servico
CREATE TABLE Servico (
    idReserva INT,
    tipoServico VARCHAR(50),
    PRIMARY KEY (idReserva, tipoServico),
    FOREIGN KEY (idReserva) REFERENCES Reserva(idReserva),
    FOREIGN KEY (tipoServico) REFERENCES TipoServico(tipo)
);

-- Tabela Cliente
CREATE TABLE Cliente (
    CPF VARCHAR(14) PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    Telefone VARCHAR(15),
    Email VARCHAR(100)
);

-- Tabela Reserva
CREATE TABLE Reserva (
    idReserva INT PRIMARY KEY AUTO_INCREMENT,
    CPF_cliente VARCHAR(14) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    idRecepcionista INT,
    idQuarto INT,
    FOREIGN KEY (idRecepcionista) REFERENCES Recepcionista(idFuncionario),
    FOREIGN KEY (idQuarto) REFERENCES Quarto(numero_quarto),
    FOREIGN KEY (CPF_cliente) REFERENCES Cliente(CPF)
);

-- Gatilho para atualizar reservas do recepcionista
DELIMITER $$
CREATE TRIGGER atualizar_reservas_recepcionista
AFTER INSERT ON Reserva
FOR EACH ROW
BEGIN
    UPDATE Recepcionista
    SET ReservasRealizadas = ReservasRealizadas + 1
    WHERE idFuncionario = NEW.idRecepcionista;
    
    UPDATE Quarto
    SET status = 'Ocupado'
    WHERE numero_quarto = NEW.idQuarto;
END$$
DELIMITER ;

-- Consulta por substring
(SELECT f.idFuncionario, f.Nome, f.Salario, 'Recepcionista' AS Categoria, r.ReservasRealizadas AS Reservas
	FROM Funcionario f
	JOIN Recepcionista r ON f.idFuncionario = r.idFuncionario
    WHERE LOWER(f.Nome) LIKE LOWER("%Jo%"))
UNION
(SELECT f.idFuncionario, f.Nome, f.Salario, 'Camareira' AS Categoria, NULL AS Reservas
	FROM Funcionario f
	JOIN Camareira c ON f.idFuncionario = c.idFuncionario
	WHERE LOWER(f.Nome) LIKE LOWER("%Jo%"))
ORDER BY Nome;

-- Tipos de join
-- (INNER) JOIN
SELECT r.idReserva, q.numero_quarto, r.data_inicio, r.data_fim, 
                       q.status, p.valor
                FROM Reserva r
                JOIN Quarto q ON r.idQuarto = q.numero_quarto
                JOIN Pagamento p ON r.idReserva = p.idReserva
                WHERE r.CPF_cliente = %s
                GROUP BY r.idReserva
ORDER BY Nome;
-- LEFT JOIN
SELECT q.numero_quarto, q.numero_camas, q.adicionais, q.status, q.preco, c.idFuncionario
    FROM Quarto q
    LEFT JOIN Camareira c ON q.numero_quarto = c.idQuarto
    ORDER BY q.numero_quarto;

-- Quantificador existencial
SELECT 1 FROM Quarto WHERE EXISTS (SELECT 1 FROM Quarto WHERE status = 'Disponível');

-- Having + groupby + ordenação
SELECT f.idFuncionario, f.Nome, f.Salario, COUNT(r.idReserva) as "Quantidade de Reservas", 'Recepcionista' AS Categoria
    FROM Reserva r 
    JOIN Funcionario f ON f.idFuncionario = r.idRecepcionista 
    WHERE LOWER(f.Nome) LIKE ("%j%")
    GROUP BY f.idFuncionario
    HAVING COUNT(r.idReserva) > 0
    ORDER BY COUNT(r.idReserva) ASC;