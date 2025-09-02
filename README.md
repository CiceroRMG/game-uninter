# Brainrot Platformer Demo

Uma demo de plataforma 2D em Pygame com estética "Brainrot": estímulos visuais rápidos, sons repetitivos e humor caótico. Personagem: Tum Tum Sahur.

---

## Visão Geral
O objetivo: atravessar o nível, derrotar inimigos NightBorne, coletar “dopaminas” (moedas) e abrir o portão final. Há HUD de vida e score, animações GIF (com Pillow), plataformas estáticas e flutuantes.

---

## Prints

<p align="center">
  <img src="assets\prints\inicial.png" alt="Menu Principal" width="48%" style="border-radius: 15px;">
  <img src="assets\prints\game1.png" alt="Ação no Jogo" width="48%" style="border-radius: 15px;">
</p>
<p align="center">
  <img src="assets\prints\game2.png" alt="Pulando" width="48%" style="border-radius: 15px;">
  <img src="assets\prints\gameover.png" alt="Game over" width="48%" style="border-radius: 15px;">
</p>

---

## Principais Funcionalidades
- Loop de jogo + gerenciador de cenas (menu, jogo, fim)
- Player: movimento lateral, pulo, ataque, gravidade, invulnerabilidade breve após dano
- Inimigos NightBorne com patrulha, animações (idle/run/attack/hurt/death)
- Coletáveis que aumentam pontuação
- Plantas animadas (decoração)
- Portão abre ao eliminar todos inimigos
- HUD (vida + score)
- Sistema básico de áudio
- Suporte a build standalone (PyInstaller)

---

## Controles
| Tecla | Ação |
|-------|------|
| A / ← | Andar esquerda |
| D / → | Andar direita |
| Espaço | Pular |
| J | Atacar |
| Esc | Sair |

(Ajuste aqui se seu main usa outras teclas.)

---

## Estrutura de Pastas (resumida)
```
assets/
  images/        # Sprites, GIFs, tiles, plantas
  fonts/         # Fontes (ex: Kaph)
  sounds/        # Efeitos / música (se usados)
src/
  main.py
  settings.py
  core/          # SceneManager etc.
  entities/      # Player, inimigos, plataformas, coletáveis
  levels/        # level1.py
  ui/            # HUD
```

---

## Dependências
Lista em requirements.txt:
```
pygame==2.6.1
Pillow
```
Pillow é necessário para animar GIFs. Sem ele, inimigos ficam estáticos.

Instalar (ambiente virtual recomendado):
```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Executar em Desenvolvimento
```
python -m src.main
```

---

## Build Windows (EXE)
PowerShell (na raiz do projeto):
```
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --clean --noconfirm ^
  --name BrainRotGame ^
  --noconsole ^
  --add-data "assets\images;assets/images" ^
  --add-data "assets\fonts;assets/fonts" ^
  --add-data "assets\sounds;assets/sounds" ^
  src\main.py
```
Executável: `dist/BrainRotGame/BrainRotGame.exe`

Gerar ZIP no windows:
```
powershell -command "Compress-Archive -Path 'dist\\BrainRotGame\\*' -DestinationPath 'BrainRotGame_windows.zip' -Force"
```

Se usar PowerShell com quebras de linha, troque ^ por acento grave (`) ou deixe tudo em uma única linha.

---

## Problemas Comuns
| Sintoma | Causa | Solução |
|---------|-------|---------|
| GIF parado | Pillow ausente | pip install Pillow |
| Fonte não carrega | Caminho errado | Verificar settings.FONT_DIR |
| Assets faltando no EXE | --add-data incompleto | Conferir caminhos |
| Tela preta no EXE | Erro silencioso | Rodar versão com console (remova --noconsole) |
| Porta não abre | Inimigo vivo fora da tela | Eliminar todos os NightBorne |

---