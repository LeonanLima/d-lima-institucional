"""
NBR 6120:2019 - Tabelas de cargas acidentais por uso/ocupacao
Material do Prof. Matheus Roman Carini - Estrutural na Real
"""

QK_USO = {
    "dormitorio": 1.5, "sala": 1.5, "corredor_interno": 1.5,
    "banheiro": 1.5, "cozinha": 1.5, "area_servico": 2.0,
    "corredor_comum": 3.0, "escada_comum": 3.0,
    "garagem_leve": 3.0, "garagem_pesada": 5.0,
    "sacada_residencial": 2.5, "cobertura_manutencao": 1.0,
    "barrilete": 1.5, "escritorio": 2.0, "sala_reuniao": 3.0,
    "biblioteca_leitura": 2.5, "biblioteca_deposito": 4.0,
    "loja_terreo": 4.0, "deposito_geral": 4.0, "restaurante": 3.0,
    "hospital_enfermaria": 2.0, "hospital_cirurgia": 3.0,
    "hospital_corredor": 4.0, "industria_leve": 3.0,
    "industria_pesada": 6.0, "sala_aula": 3.0, "corredor_escola": 3.0,
    "cobertura_inacessivel": 0.25, "cobertura_acesso": 1.0,
    "cobertura_jardim": 2.0,
}

PESO_ESPECIFICO = {
    "concreto_armado": 25.0, "concreto_simples": 24.0,
    "argamassa_cp": 21.0, "argamassa_cal": 19.0, "argamassa_gesso": 15.0,
    "aco": 77.8, "ceramica_lajota": 18.0, "porcelanato": 23.0,
    "granito": 28.5, "vidro": 26.0, "madeira_pinus": 6.0,
    "madeira_eucalipto": 10.0, "tijolo_macico": 19.0,
    "alvenaria_bloco9": 1.9, "alvenaria_bloco14": 2.4,
    "alvenaria_bloco19": 3.0, "alvenaria_bloco_conc14": 3.0,
    "alvenaria_bloco_conc19": 4.0,
}

REVESTIMENTO = {
    "contrapiso_ceramica": 1.00, "contrapiso_porcelanato": 1.10,
    "forro_gesso": 0.15, "forro_pvc": 0.10,
    "impermeabilizacao": 0.05, "regularizacao": 0.50,
}

PSI2 = {
    "residencial": 0.3, "comercial": 0.4,
    "biblioteca": 0.6, "garagem": 0.6, "cobertura": 0.0,
}

REACOES_LAJE_BIDIR = {
    1:    {"rx": 0.1103, "ry": 0.4299, "rxe": None,   "rye": None  },
    2:    {"rx": 0.0482, "ry": 0.3520, "rxe": None,   "rye": 0.5867},
    "2A": {"rx": 0.1709, "ry": 0.2988, "rxe": 0.2849, "rye": None  },
    3:    {"rx": None,   "ry": 0.2754, "rxe": None,   "rye": 0.4842},
    4:    {"rx": 0.0827, "ry": 0.3224, "rxe": 0.1379, "rye": 0.5374},
    5:    {"rx": None,   "ry": None,   "rxe": 0.0742, "rye": 0.4623},
    6:    {"rx": None,   "ry": None,   "rxe": 0.1103, "rye": 0.4299},
}

def qk_por_uso(uso: str) -> float:
    v = QK_USO.get(uso.lower())
    if v is None:
        raise ValueError(f"Uso nao encontrado: {uso}. Opcoes: {list(QK_USO.keys())}")
    return v

def carga_parede(tipo_bloco: str, h_parede_m: float) -> float:
    """Carga linear de parede sobre viga [kN/m] - NBR 16868-1:2020"""
    gamma = PESO_ESPECIFICO.get(f"alvenaria_{tipo_bloco}")
    if gamma is None:
        raise ValueError(f"Bloco nao encontrado: {tipo_bloco}")
    return round(gamma * h_parede_m, 2)

def pp_laje_macica(h_m: float) -> float:
    return round(25.0 * h_m, 2)

def pp_viga(b_cm: float, h_cm: float) -> float:
    return round(25.0 * (b_cm/100) * (h_cm/100), 2)

def pp_pilar_por_metro(b_cm: float, h_cm: float) -> float:
    return round(25.0 * (b_cm/100) * (h_cm/100), 2)
