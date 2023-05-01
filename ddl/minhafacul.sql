-- SQL de criação do banco de dados para a ferramenta minhaFacul
-- Alexandre CASTILHO 21/04/2023
-- FACULDADE definition

CREATE TABLE FACULDADE (
	FACULDADE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	FACULADE TEXT(300),
	LOCAL_TXT TEXT(300),
	LOCAL_LAT REAL,
	LOCAL_LON REAL,
	CONSTRAINT FACULDADE_UN UNIQUE (FACULADE)
);


-- CURSO definition

CREATE TABLE CURSO (
	CURSO_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	CURSO TEXT(300),
	CONSTRAINT CURSO_UN UNIQUE (CURSO)
);


-- USUARIO definition

CREATE TABLE USUARIO (
	USUARIO_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	EMAIL TEXT(300),
	SENHA_SHA256 TEXT(64),
	RECUPERA_SENHA INTEGER DEFAULT (0),
	ADMINISTRADOR INTEGER DEFAULT (0),
	CURSO_ID INTEGER,
	LOCAL_TXT TEXT(300),
	LOCAL_LAT REAL,
	LOCAL_LON REAL,
	CONSTRAINT USUARIO_UN UNIQUE (EMAIL),
	CONSTRAINT USUARIO_FK FOREIGN KEY (CURSO_ID) REFERENCES CURSO(CURSO_ID)
);


-- HISTORICO definition

CREATE TABLE HISTORICO (
	HISTORICO_ID INTEGER PRIMARY KEY AUTOINCREMENT,
	FACULDADE_ID INTEGER,
	CURSO_ID INTEGER,
	ANO INTEGER,
	VAGAS INTEGER,
	CANDIDATOS INTEGER,
	CONSTRAINT HISTORICO_UN UNIQUE (FACULDADE_ID,CURSO_ID,ANO),
	CONSTRAINT HISTORICO_FK FOREIGN KEY (FACULDADE_ID) REFERENCES FACULDADE(FACULDADE_ID),
	CONSTRAINT HISTORICO_FK_1 FOREIGN KEY (CURSO_ID) REFERENCES CURSO(CURSO_ID)
);


-- Comparativo entre faculdades para o ano atual e ultimos dois

CREATE VIEW COMPARATIVO AS
SELECT A.FACULDADE_ID, A.CURSO_ID, D.FACULADE, E.CURSO, D.LOCAL_LAT, D.LOCAL_LON,
	CAST(CAST(A.CANDIDATOS AS REAL) / CAST(A.VAGAS AS REAL) AS REAL(10,2)) AS CPV,
	CAST(CAST(B.CANDIDATOS AS REAL) / CAST(B.VAGAS AS REAL) AS REAL(10,2)) AS CPV_1,
	CAST(CAST(C.CANDIDATOS AS REAL) / CAST(C.VAGAS AS REAL) AS REAL(10,2)) AS CPV_2
FROM
    (SELECT * FROM HISTORICO WHERE ANO = strftime('%Y', 'now')) AS A
LEFT JOIN
    (SELECT * FROM HISTORICO WHERE ANO = strftime('%Y', 'now')-1) AS B
USING (FACULDADE_ID, CURSO_ID)
LEFT JOIN
    (SELECT * FROM HISTORICO WHERE ANO = strftime('%Y', 'now')-2) AS C
USING (FACULDADE_ID, CURSO_ID)
LEFT JOIN
    FACULDADE AS D
USING (FACULDADE_ID)
LEFT JOIN
    CURSO AS E
USING (CURSO_ID)

-- Cria um usuário administrador
INSERT INTO USUARIO	(EMAIL, SENHA_SHA256, RECUPERA_SENHA, ADMINISTRADOR, CURSO_ID)
VALUES
    ('root@root.com', '4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2', 0, 1, 0);


--#############################################################################
--#    DADOS DE EXEMPLO PARA DESENVOLVIMENTO DA FERRAMENTA USAR COM CUIDADO!  #
--#############################################################################

-- Cria dados de teste
INSERT INTO USUARIO	(EMAIL, SENHA_SHA256, RECUPERA_SENHA, ADMINISTRADOR, CURSO_ID, LOCAL_TXT, LOCAL_LAT, LOCAL_LON)
VALUES
    ('eu@dot.com', '4d0282941aaf2d694ddaa24fca75e503c73ab16fff3884cac12f39f882bc60cb', 0, 0, 1, '', 0, 0);

INSERT INTO CURSO (CURSO) VALUES
	('Eixo Computação'),
	('Eixo Licenciaturas'),
	('Eixo de Negócios e Produção');

INSERT INTO FACULDADE (FACULADE, LOCAL_TXT, LOCAL_LAT, LOCAL_LON) VALUES
	('Faculdade 1', 'Cacapava', -23.1121, -45.7084),
	('Faculdade 2', 'Taubate', -23.0300, -45.5655),
	('Faculdade 3', 'Sao Jose dos campos', -23.1843, -45.8651);

INSERT INTO HISTORICO (FACULDADE_ID, CURSO_ID, ANO, VAGAS, CANDIDATOS)
VALUES
	(1, 1, 2023, 10, 100),
	(1, 1, 2022, 20, 200),
	(1, 1, 2021, 30, 300),
	(1, 2, 2023, 10, 6),
	(1, 2, 2022, 20, 24),
	(1, 2, 2021, 30, 31),
	(1, 3, 2023, 10, 19),
	(1, 3, 2022, 20, 9),
	(1, 3, 2021, 30, 14),
	(2, 1, 2023, 20, 101),
	(2, 1, 2022, 40, 201),
	(2, 1, 2021, 60, 301),
	(2, 2, 2023, 20, 15),
	(2, 2, 2022, 40, 38),
	(2, 2, 2021, 60, 56),
	(2, 3, 2023, 20, 17),
	(2, 3, 2022, 40, 40),
	(2, 3, 2021, 60, 99),
	(3, 1, 2023, 40, 102),
	(3, 1, 2022, 80, 202),
	(3, 1, 2021, 120, 302),
	(3, 2, 2023, 40, 35),
	(3, 2, 2022, 80, 84),
	(3, 2, 2021, 120, 116),
	(3, 3, 2023, 40, 79),
	(3, 3, 2022, 80, 16),
	(3, 3, 2021, 120, 235);
