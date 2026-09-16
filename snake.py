import pygame
import random
import time
import os
import array

# Inicializa o Pygame e o áudio
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# Dimensões
LARGURA = 800
ALTURA = 600
TAMANHO_BLOCO = 20

# Configurações de Velocidade
VELOCIDADE_INICIAL = 8
ACELERACAO = 0.5
VELOCIDADE_MINIMA = 6
VELOCIDADE_MAXIMA = 25

NOME_ARQUIVO_RECORDE = "recorde.txt"

# --- PALETAS DE CORES GERAIS ---
COR_MACA_COMUM = (244, 63, 94)
COR_MACA_DOURADA = (250, 204, 21)
COR_PIMENTA_LENTO = (192, 132, 252)
COR_FRUTA_FANTASMA = (56, 189, 248)
COR_FRUTA_IMA = (168, 85, 247)

COR_MACA_BRILHO = (255, 255, 255)
COR_FOLHA = (74, 222, 128)
COR_CABINHO = (180, 83, 9)

COR_OBSTACULO = (51, 65, 85)
COR_OBSTACULO_BORDA = (100, 116, 139)

COR_TEXTO_BRANCO = (248, 250, 252)
COR_TEXTO_MUTED = (148, 163, 184)
COR_TEXTO_SOMBRA = (2, 6, 23)
COR_CARD_BG = (20, 29, 47)
COR_CARD_BORDA = (51, 65, 85)

# --- CONFIGURAÇÃO DE FRUTAS ---
CONFIG_FRUTAS = {
    "comum": {"nome": "Maçã Vermelha", "cor": COR_MACA_COMUM, "pontos_req": 0, "peso_base": 100, "efeito": "+1 Ponto | Aumenta velocidade"},
    "dourada": {"nome": "Maçã Dourada", "cor": COR_MACA_DOURADA, "pontos_req": 5, "peso_base": 20, "efeito": "+3 Pontos extra"},
    "lento": {"nome": "Pimenta Violeta", "cor": COR_PIMENTA_LENTO, "pontos_req": 10, "peso_base": 15, "efeito": "+1 Ponto | Desacelera a cobra"},
    "ima": {"nome": "Fruta Roxa (Ímã)", "cor": COR_FRUTA_IMA, "pontos_req": 15, "peso_base": 10, "efeito": "Atrai todas as frutas por 6s"},
    "fantasma": {"nome": "Fruta Azul (Fantasma)", "cor": COR_FRUTA_FANTASMA, "pontos_req": 25, "peso_base": 5, "efeito": "Atravessa paredes/corpo por 5s"}
}

# --- SKINS ---
SKINS = {
    "Verde Neon": {"requisito_recorde": 0, "cabeca": (34, 197, 94), "corpo": (22, 163, 74), "olhos": (255, 255, 255), "pupila": (15, 23, 42), "lingua": (239, 68, 68)},
    "Cobra Roxa": {"requisito_recorde": 10, "cabeca": (192, 132, 252), "corpo": (147, 51, 234), "olhos": (255, 255, 255), "pupila": (15, 23, 42), "lingua": (74, 222, 128)},
    "Cobra de Fogo": {"requisito_recorde": 25, "cabeca": (251, 146, 60), "corpo": (225, 29, 72), "olhos": (254, 240, 138), "pupila": (69, 10, 10), "lingua": (250, 204, 21)},
    "Cobra Cyberpunk": {"requisito_recorde": 40, "cabeca": (34, 211, 238), "corpo": (37, 99, 235), "olhos": (255, 255, 255), "pupila": (15, 23, 42), "lingua": (244, 114, 182)},
    "Cobra Dourada HD": {"requisito_recorde": 60, "cabeca": (253, 224, 71), "corpo": (202, 138, 4), "olhos": (255, 255, 255), "pupila": (66, 32, 6), "lingua": (239, 68, 68)},
    "Cobra Fantasma": {"requisito_recorde": 80, "cabeca": (226, 232, 240), "corpo": (148, 163, 184), "olhos": (56, 189, 248), "pupila": (15, 23, 42), "lingua": (192, 132, 252)}
}

# --- FUNÇÕES DE GERAR OBSTÁCULOS DOS MAPAS ---
def gerar_mapa_arena():
    obs = []
    for i in range(5):
        obs.extend([[100 + i*20, 100], [100, 100 + i*20]])
        obs.extend([[700 - i*20, 100], [700, 100 + i*20]])
        obs.extend([[100 + i*20, 500], [100, 500 - i*20]])
        obs.extend([[700 - i*20, 500], [700, 500 - i*20]])
    return obs

def gerar_mapa_labirinto():
    obs = []
    for y in range(120, 480, 20):
        obs.append([260, y])
        obs.append([540, y])
    return obs

def gerar_mapa_prisao():
    obs = []
    for x in range(60, 740, 20):
        if x not in [200, 600]:
            obs.append([x, 300])
    for y in range(80, 540, 20):
        if y not in [180, 420]:
            obs.append([400, y])
    return obs

def gerar_mapa_campo_minado():
    obs = []
    for x in range(100, 720, 60):
        for y in range(100, 520, 60):
            if [x, y] != [200, 200]:
                obs.append([x, y])
    return obs

def gerar_mapa_espiral():
    obs = []
    for x in range(200, 620, 20): obs.append([x, 140])
    for y in range(140, 480, 20): obs.append([600, y])
    for x in range(260, 620, 20): obs.append([x, 460])
    for y in range(220, 460, 20): obs.append([260, y])
    for x in range(260, 520, 20): obs.append([x, 220])
    return obs

# --- MAPAS COM CORES DE BACKGROUND ÚNICAS ---
MAPAS = {
    "Campo Aberto": {
        "requisito_recorde": 0,
        "obstaculos": [],
        "fundo": (11, 15, 25),
        "grade1": (18, 24, 38),
        "grade2": (14, 19, 31),
        "borda": (30, 41, 59)
    },
    "Arena Classica": {
        "requisito_recorde": 15,
        "obstaculos": gerar_mapa_arena(),
        "fundo": (20, 10, 25),
        "grade1": (32, 16, 40),
        "grade2": (25, 12, 32),
        "borda": (88, 28, 112)
    },
    "O Labirinto": {
        "requisito_recorde": 35,
        "obstaculos": gerar_mapa_labirinto(),
        "fundo": (8, 22, 28),
        "grade1": (12, 34, 44),
        "grade2": (9, 27, 35),
        "borda": (14, 116, 144)
    },
    "A Prisão": {
        "requisito_recorde": 50,
        "obstaculos": gerar_mapa_prisao(),
        "fundo": (28, 15, 10),
        "grade1": (42, 24, 16),
        "grade2": (34, 18, 12),
        "borda": (180, 83, 9)
    },
    "Campo Minado": {
        "requisito_recorde": 70,
        "obstaculos": gerar_mapa_campo_minado(),
        "fundo": (28, 10, 15),
        "grade1": (44, 16, 24),
        "grade2": (35, 12, 18),
        "borda": (225, 29, 72)
    },
    "Caos Espiral": {
        "requisito_recorde": 90,
        "obstaculos": gerar_mapa_espiral(),
        "fundo": (15, 8, 30),
        "grade1": (26, 14, 50),
        "grade2": (20, 10, 38),
        "borda": (147, 51, 234)
    }
}

lista_nomes_skins = list(SKINS.keys())
lista_nomes_mapas = list(MAPAS.keys())
indice_skin_atual = 0
indice_mapa_atual = 0

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Snake Game - Hardcore Edition')

relogio = pygame.time.Clock()
fonte_micro = pygame.font.SysFont("trebuchetms", 12, bold=True)
fonte_pequena = pygame.font.SysFont("trebuchetms", 14, bold=True)
fonte_media = pygame.font.SysFont("trebuchetms", 18, bold=True)
fonte_grande = pygame.font.SysFont("trebuchetms", 36, bold=True)

def gerar_som(freq_inicio, freq_fim, duracao_ms, volume=0.3):
    sample_rate = 22050
    n_samples = int(sample_rate * (duracao_ms / 1000.0))
    buf = array.array('h')
    for i in range(n_samples):
        t = float(i) / n_samples
        freq = freq_inicio + (freq_fim - freq_inicio) * t
        periodo = sample_rate / freq
        val = 32767 if (int(i / (periodo / 2)) % 2 == 0) else -32767
        buf.append(int(val * volume))
    return pygame.mixer.Sound(buffer=buf)

som_comer_comum = gerar_som(400, 800, 80)
som_comer_especial = gerar_som(600, 1200, 150)
som_game_over = gerar_som(300, 100, 300)
som_clique = gerar_som(800, 800, 30)

def carregar_recorde():
    if os.path.exists(NOME_ARQUIVO_RECORDE):
        try:
            with open(NOME_ARQUIVO_RECORDE, "r") as arq:
                return int(arq.read().strip())
        except ValueError:
            return 0
    return 0

def salvar_recorde(novo_recorde):
    with open(NOME_ARQUIVO_RECORDE, "w") as arq:
        arq.write(str(novo_recorde))

recorde_global = carregar_recorde()

def desenhar_texto_com_sombra(texto, fonte, cor, x, y, centralizado=True):
    surf_sombra = fonte.render(texto, True, COR_TEXTO_SOMBRA)
    surf_texto = fonte.render(texto, True, cor)
    rect_sombra = surf_sombra.get_rect()
    rect_texto = surf_texto.get_rect()

    if centralizado:
        rect_sombra.center = (x + 2, y + 2)
        rect_texto.center = (x, y)
    else:
        rect_sombra.topleft = (x + 2, y + 2)
        rect_texto.topleft = (x, y)

    tela.blit(surf_sombra, rect_sombra)
    tela.blit(surf_texto, rect_texto)

# --- DESENHO DE FUNDO ADAPTATIVO POR MAPA ---
def desenhar_fundo(mapa_obj=None):
    if mapa_obj is None:
        mapa_obj = MAPAS[lista_nomes_mapas[indice_mapa_atual]]

    tela.fill(mapa_obj["fundo"])
    for y in range(0, ALTURA, TAMANHO_BLOCO):
        for x in range(0, LARGURA, TAMANHO_BLOCO):
            cor = mapa_obj["grade1"] if ((x // TAMANHO_BLOCO) + (y // TAMANHO_BLOCO)) % 2 == 0 else mapa_obj["grade2"]
            pygame.draw.rect(tela, cor, [x, y, TAMANHO_BLOCO, TAMANHO_BLOCO])
    pygame.draw.rect(tela, mapa_obj["borda"], [0, 0, LARGURA, ALTURA], width=2)

def desenhar_fruta_glow(x, y, tipo):
    centro_x = int(x + TAMANHO_BLOCO / 2)
    centro_y = int(y + TAMANHO_BLOCO / 2)
    raio = TAMANHO_BLOCO // 2 - 1

    cor_base = CONFIG_FRUTAS[tipo]["cor"]

    glow_surf = pygame.Surface((TAMANHO_BLOCO * 2, TAMANHO_BLOCO * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*cor_base, 40), (TAMANHO_BLOCO, TAMANHO_BLOCO), raio + 5)
    pygame.draw.circle(glow_surf, (*cor_base, 80), (TAMANHO_BLOCO, TAMANHO_BLOCO), raio + 2)
    tela.blit(glow_surf, (centro_x - TAMANHO_BLOCO, centro_y - TAMANHO_BLOCO))

    pygame.draw.circle(tela, cor_base, (centro_x, centro_y), raio)
    pygame.draw.circle(tela, COR_MACA_BRILHO, (centro_x - 3, centro_y - 3), 2)
    pygame.draw.line(tela, COR_CABINHO, (centro_x, centro_y - raio), (centro_x + 2, centro_y - raio - 4), 2)
    pygame.draw.ellipse(tela, COR_FOLHA, [centro_x + 1, centro_y - raio - 4, 5, 3])

def desenhar_obstaculos(obstaculos):
    for obs in obstaculos:
        rect = pygame.Rect(obs[0], obs[1], TAMANHO_BLOCO, TAMANHO_BLOCO)
        pygame.draw.rect(tela, COR_OBSTACULO, rect, border_radius=4)
        pygame.draw.rect(tela, COR_OBSTACULO_BORDA, rect, width=2, border_radius=4)

def desenhar_cobra(corpo_cobra, direcao, skin, bloqueada=False, modo_fantasma=False, tempo_fantasma_restante=0):
    piscando = modo_fantasma and tempo_fantasma_restante <= 1.5 and int(time.time() * 10) % 2 == 0

    for i, bloco in enumerate(corpo_cobra):
        is_cabeca = (i == len(corpo_cobra) - 1)
        cor = skin["cabeca"] if is_cabeca else skin["corpo"]

        if bloqueada:
            cor = (51, 65, 85)
        elif modo_fantasma:
            cor = (186, 230, 253) if piscando else (56, 189, 248)

        rect = pygame.Rect(bloco[0], bloco[1], TAMANHO_BLOCO, TAMANHO_BLOCO)
        
        if modo_fantasma and not bloqueada:
            surf_transparente = pygame.Surface((TAMANHO_BLOCO, TAMANHO_BLOCO), pygame.SRCALPHA)
            pygame.draw.rect(surf_transparente, (*cor, 160), (0, 0, TAMANHO_BLOCO, TAMANHO_BLOCO), border_radius=6)
            tela.blit(surf_transparente, (bloco[0], bloco[1]))
        else:
            pygame.draw.rect(tela, cor, rect, border_radius=6)

        if is_cabeca:
            cx, cy = bloco[0], bloco[1]
            if direcao == "DIREITA":
                olho1, olho2 = (cx + 13, cy + 5), (cx + 13, cy + 13)
                lingua_ini, lingua_fim = (cx + 20, cy + 10), (cx + 25, cy + 10)
            elif direcao == "ESQUERDA":
                olho1, olho2 = (cx + 5, cy + 5), (cx + 5, cy + 13)
                lingua_ini, lingua_fim = (cx, cy + 10), (cx - 5, cy + 10)
            elif direcao == "CIMA":
                olho1, olho2 = (cx + 5, cy + 5), (cx + 13, cy + 5)
                lingua_ini, lingua_fim = (cx + 10, cy), (cx + 10, cy - 5)
            else:
                olho1, olho2 = (cx + 5, cy + 13), (cx + 13, cy + 13)
                lingua_ini, lingua_fim = (cx + 10, cy + 20), (cx + 10, cy + 25)

            if direcao != "PARADO":
                cor_lingua = (100, 116, 139) if bloqueada else skin["lingua"]
                pygame.draw.line(tela, cor_lingua, lingua_ini, lingua_fim, 2)

            cor_olhos = (148, 163, 184) if bloqueada else skin["olhos"]
            cor_pupila = (15, 23, 42) if bloqueada else skin["pupila"]
            for ox, oy in [olho1, olho2]:
                pygame.draw.circle(tela, cor_olhos, (ox, oy), 4)
                pygame.draw.circle(tela, cor_pupila, (ox, oy), 2)

def mostrar_hud(pontos, recorde, velocidade, nome_mapa, t_fantasma, t_ima, cor_borda):
    hud_surf = pygame.Surface((LARGURA, 38), pygame.SRCALPHA)
    hud_surf.fill((11, 15, 25, 220))
    tela.blit(hud_surf, (0, 0))
    pygame.draw.line(tela, cor_borda, (0, 38), (LARGURA, 38), 2)

    desenhar_texto_com_sombra(f"PONTOS: {pontos}", fonte_media, COR_TEXTO_BRANCO, 70, 18)
    desenhar_texto_com_sombra(f"MAPA: {nome_mapa.upper()}", fonte_media, (147, 51, 234), LARGURA // 2 - 120, 18)
    desenhar_texto_com_sombra(f"RECORDE: {recorde}", fonte_media, COR_MACA_DOURADA, LARGURA // 2 + 60, 18)
    desenhar_texto_com_sombra(f"VEL: {int(velocidade)}", fonte_media, (34, 211, 238), LARGURA - 50, 18)

    pos_x_buff = LARGURA // 2 + 180
    if t_fantasma > 0:
        desenhar_texto_com_sombra(f"FANTASMA: {t_fantasma:.1f}s", fonte_pequena, COR_FRUTA_FANTASMA, pos_x_buff, 18)
        pos_x_buff += 110
    if t_ima > 0:
        desenhar_texto_com_sombra(f"IMÃ: {t_ima:.1f}s", fonte_pequena, COR_FRUTA_IMA, pos_x_buff, 18)

def gerar_posicao_valida(posicoes_ocupadas):
    while True:
        x = round(random.randrange(0, LARGURA - TAMANHO_BLOCO) / 20.0) * 20.0
        y = round(random.randrange(40, ALTURA - TAMANHO_BLOCO) / 20.0) * 20.0
        if [x, y] not in posicoes_ocupadas:
            return x, y

def criar_fruta(posicoes_ocupadas, pontuacao_atual):
    x, y = gerar_posicao_valida(posicoes_ocupadas)
    
    frutas_disponiveis = []
    pesos = []

    for chave, config in CONFIG_FRUTAS.items():
        if pontuacao_atual >= config["pontos_req"]:
            frutas_disponiveis.append(chave)
            if chave == "comum":
                peso_calculado = max(10, config["peso_base"] - (pontuacao_atual * 1.5))
            else:
                peso_calculado = config["peso_base"] + (pontuacao_atual * 0.8)
            pesos.append(peso_calculado)

    tipo_escolhido = random.choices(frutas_disponiveis, weights=pesos, k=1)[0]
    return {"pos": [x, y], "tipo": tipo_escolhido}

def menu_principal():
    global recorde_global, indice_skin_atual, indice_mapa_atual
    rodando = True
    while rodando:
        nome_mapa = lista_nomes_mapas[indice_mapa_atual]
        mapa_obj = MAPAS[nome_mapa]

        # Fundo dinâmico conforme o mapa selecionado
        desenhar_fundo(mapa_obj)

        nome_skin = lista_nomes_skins[indice_skin_atual]
        skin_obj = SKINS[nome_skin]
        skin_bloqueada = recorde_global < skin_obj["requisito_recorde"]
        mapa_bloqueado = recorde_global < mapa_obj["requisito_recorde"]

        desenhar_texto_com_sombra("SNAKE GAME ULTIMATE", fonte_grande, (34, 197, 94), LARGURA // 2, 40)

        # Card de Seleção de Skin
        card_skin = pygame.Rect(LARGURA // 2 - 360, 90, 340, 200)
        pygame.draw.rect(tela, COR_CARD_BG, card_skin, border_radius=12)
        pygame.draw.rect(tela, COR_CARD_BORDA, card_skin, width=2, border_radius=12)

        cobra_demo = [[LARGURA // 2 - 220, 140], [LARGURA // 2 - 200, 140], [LARGURA // 2 - 180, 140]]
        desenhar_cobra(cobra_demo, "DIREITA", skin_obj, skin_bloqueada)

        desenhar_texto_com_sombra(f"< SKIN: {nome_skin} >", fonte_media, COR_TEXTO_BRANCO, LARGURA // 2 - 190, 190)
        txt_s_status = f"REQ: {skin_obj['requisito_recorde']} Pts" if skin_bloqueada else "DESBLOQUEADO"
        cor_s_status = (239, 68, 68) if skin_bloqueada else (34, 197, 94)
        desenhar_texto_com_sombra(txt_s_status, fonte_pequena, cor_s_status, LARGURA // 2 - 190, 240)

        # Card de Seleção de Mapa
        card_mapa = pygame.Rect(LARGURA // 2 + 20, 90, 340, 200)
        pygame.draw.rect(tela, COR_CARD_BG, card_mapa, border_radius=12)
        pygame.draw.rect(tela, COR_CARD_BORDA, card_mapa, width=2, border_radius=12)

        desenhar_texto_com_sombra(f"^ MAPA: {nome_mapa} v", fonte_media, COR_TEXTO_BRANCO, LARGURA // 2 + 190, 140)
        txt_m_status = f"REQ: {mapa_obj['requisito_recorde']} Pts" if mapa_bloqueado else "DESBLOQUEADO"
        cor_m_status = (239, 68, 68) if mapa_bloqueado else (34, 197, 94)
        desenhar_texto_com_sombra(txt_m_status, fonte_pequena, cor_m_status, LARGURA // 2 + 190, 240)

        # Card Guia de Frutas
        card_frutas = pygame.Rect(LARGURA // 2 - 360, 305, 720, 175)
        pygame.draw.rect(tela, COR_CARD_BG, card_frutas, border_radius=12)
        pygame.draw.rect(tela, COR_CARD_BORDA, card_frutas, width=2, border_radius=12)

        desenhar_texto_com_sombra("GUIA DE FRUTAS & REQUISITOS", fonte_media, COR_TEXTO_BRANCO, LARGURA // 2, 325)

        y_item = 350
        for chave, item in CONFIG_FRUTAS.items():
            desenhar_fruta_glow(LARGURA // 2 - 330, y_item, chave)
            req_texto = f"(Mínimo: {item['pontos_req']} Pts)" if item['pontos_req'] > 0 else "(Início)"
            desenhar_texto_com_sombra(f"{item['nome']} {req_texto}", fonte_pequena, item["cor"], LARGURA // 2 - 300, y_item + 10, centralizado=False)
            desenhar_texto_com_sombra(f"- {item['efeito']}", fonte_micro, COR_TEXTO_MUTED, LARGURA // 2 + 50, y_item + 10, centralizado=False)
            y_item += 23

        # Rodapé
        desenhar_texto_com_sombra("Pressione [ESPAÇO] para Jogar", fonte_media, COR_TEXTO_BRANCO, LARGURA // 2, 500)
        desenhar_texto_com_sombra("Controles: [SETAS ESQ/DIR] Skin | [SETAS CIMA/BAIXO] Mapa", fonte_micro, COR_TEXTO_MUTED, LARGURA // 2, 535)
        desenhar_texto_com_sombra(f"Seu Recorde Salvo: {recorde_global} Pts", fonte_pequena, COR_MACA_DOURADA, LARGURA // 2, 565)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not skin_bloqueada and not mapa_bloqueado:
                        som_clique.play()
                        return True
                    else:
                        som_game_over.play()
                elif event.key == pygame.K_RIGHT:
                    indice_skin_atual = (indice_skin_atual + 1) % len(lista_nomes_skins)
                    som_clique.play()
                elif event.key == pygame.K_LEFT:
                    indice_skin_atual = (indice_skin_atual - 1) % len(lista_nomes_skins)
                    som_clique.play()
                elif event.key == pygame.K_DOWN:
                    indice_mapa_atual = (indice_mapa_atual + 1) % len(lista_nomes_mapas)
                    som_clique.play()
                elif event.key == pygame.K_UP:
                    indice_mapa_atual = (indice_mapa_atual - 1) % len(lista_nomes_mapas)
                    som_clique.play()

def jogo():
    global recorde_global
    game_close = False
    em_pausa = False
    som_game_over_tocado = False

    skin_atual = SKINS[lista_nomes_skins[indice_skin_atual]]
    nome_mapa = lista_nomes_mapas[indice_mapa_atual]
    mapa_atual = MAPAS[nome_mapa]

    x, y = 200.0, 200.0
    x_mudanca, y_mudanca = 0, 0
    direcao, proxima_direcao = "PARADO", "PARADO"

    corpo_cobra = [[x, y]]
    tamanho_cobra = 1
    pontuacao = 0
    velocidade = VELOCIDADE_INICIAL

    tempo_fantasma = 0
    tempo_ima = 0

    obstaculos = list(mapa_atual["obstaculos"])

    frutas = []
    for _ in range(3):
        nova_fruta = criar_fruta(corpo_cobra + obstaculos + [f["pos"] for f in frutas], pontuacao)
        frutas.append(nova_fruta)

    tempo_anterior = time.time()

    while True:
        tempo_atual = time.time()
        delta_time = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual

        while game_close:
            if not som_game_over_tocado:
                som_game_over.play()
                som_game_over_tocado = True

            desenhar_fundo(mapa_atual)
            desenhar_texto_com_sombra("FIM DE JOGO!", fonte_grande, COR_MACA_COMUM, LARGURA // 2, ALTURA // 3)
            desenhar_texto_com_sombra("[C] Jogar Novamente   |   [M] Menu Principal", fonte_media, COR_TEXTO_BRANCO, LARGURA // 2, ALTURA // 2)

            if pontuacao > recorde_global:
                recorde_global = pontuacao
                salvar_recorde(recorde_global)

            mostrar_hud(pontuacao, recorde_global, velocidade, nome_mapa, 0, 0, mapa_atual["borda"])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        som_clique.play()
                        return
                    if event.key == pygame.K_c:
                        som_clique.play()
                        jogo()
                        return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    som_clique.play()
                    em_pausa = not em_pausa
                if not em_pausa:
                    if event.key == pygame.K_LEFT and direcao != "DIREITA":
                        proxima_direcao = "ESQUERDA"
                    elif event.key == pygame.K_RIGHT and direcao != "ESQUERDA":
                        proxima_direcao = "DIREITA"
                    elif event.key == pygame.K_UP and direcao != "BAIXO":
                        proxima_direcao = "CIMA"
                    elif event.key == pygame.K_DOWN and direcao != "CIMA":
                        proxima_direcao = "BAIXO"

        if em_pausa:
            pygame.time.wait(100)
            tempo_anterior = time.time()
            continue

        if tempo_fantasma > 0:
            tempo_fantasma = max(0, tempo_fantasma - delta_time)
        if tempo_ima > 0:
            tempo_ima = max(0, tempo_ima - delta_time)

        direcao = proxima_direcao
        if direcao == "ESQUERDA": x_mudanca, y_mudanca = -TAMANHO_BLOCO, 0
        elif direcao == "DIREITA": x_mudanca, y_mudanca = TAMANHO_BLOCO, 0
        elif direcao == "CIMA": x_mudanca, y_mudanca = 0, -TAMANHO_BLOCO
        elif direcao == "BAIXO": x_mudanca, y_mudanca = 0, TAMANHO_BLOCO

        x += x_mudanca
        y += y_mudanca

        # Teletransporte nas Bordas
        if x >= LARGURA: x = 0
        elif x < 0: x = LARGURA - TAMANHO_BLOCO
        if y >= ALTURA: y = 40
        elif y < 40: y = ALTURA - TAMANHO_BLOCO

        cabeca_cobra = [x, y]
        corpo_cobra.append(cabeca_cobra)

        if len(corpo_cobra) > tamanho_cobra:
            del corpo_cobra[0]

        # Atração pelo Ímã
        if tempo_ima > 0 and direcao != "PARADO":
            for f in frutas:
                fx, fy = f["pos"]
                if fx < x: fx += 20
                elif fx > x: fx -= 20
                if fy < y: fy += 20
                elif fy > y: fy -= 20
                
                if [fx, fy] not in obstaculos:
                    f["pos"] = [fx, fy]

        # Colisões
        if tempo_fantasma <= 0:
            for bloco in corpo_cobra[:-1]:
                if bloco == cabeca_cobra and direcao != "PARADO":
                    game_close = True

            if cabeca_cobra in obstaculos:
                game_close = True

        desenhar_fundo(mapa_atual)
        desenhar_obstaculos(obstaculos)

        for f in frutas:
            desenhar_fruta_glow(f["pos"][0], f["pos"][1], f["tipo"])

        desenhar_cobra(corpo_cobra, direcao, skin_atual, modo_fantasma=(tempo_fantasma > 0), tempo_fantasma_restante=tempo_fantasma)

        if pontuacao > recorde_global:
            recorde_global = pontuacao
            salvar_recorde(recorde_global)

        mostrar_hud(pontuacao, recorde_global, velocidade, nome_mapa, tempo_fantasma, tempo_ima, mapa_atual["borda"])
        pygame.display.update()

        # Coleta de Frutas
        for i in range(len(frutas)):
            f = frutas[i]
            if x == f["pos"][0] and y == f["pos"][1]:
                tamanho_cobra += 1
                tipo_f = f["tipo"]

                if tipo_f == "dourada":
                    pontuacao += 3
                    som_comer_especial.play()
                elif tipo_f == "lento":
                    pontuacao += 1
                    velocidade = max(VELOCIDADE_MINIMA, velocidade - 3)
                    som_comer_especial.play()
                elif tipo_f == "fantasma":
                    pontuacao += 2
                    tempo_fantasma = 5.0
                    som_comer_especial.play()
                elif tipo_f == "ima":
                    pontuacao += 2
                    tempo_ima = 6.0
                    som_comer_especial.play()
                else:
                    pontuacao += 1
                    som_comer_comum.play()
                    if velocidade < VELOCIDADE_MAXIMA:
                        velocidade += ACELERACAO

                frutas[i] = criar_fruta(corpo_cobra + obstaculos + [frutas[j]["pos"] for j in range(len(frutas)) if j != i], pontuacao)
                break

        relogio.tick(int(velocidade))

def principal():
    while True:
        if menu_principal():
            jogo()
        else:
            break
    pygame.quit()

if __name__ == "__main__":
    principal()