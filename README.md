# Brainrot Platformer Demo

Tema: "Brainrot" — estética caótica de memes, sobrecarga visual e sons repetitivos.
Personagem principal: Tum Tum Sahur.

## Funcionalidades
- Loop principal com Pygame
- Sistema de cena (menu inicial e jogo)
- Personagem jogável: movimento lateral, pulo, física básica, animação simples
- Plataformas estáticas + detecção de colisão
- Coletáveis "dopamina" que aumentam score
- Inimigos com movimento padrão (patrulha) e knockback
- Barra de vida + sistema de game over / restart
- Efeitos visuais: tremor de câmera leve quando leva dano
- Sistema de áudio

## Como rodar
Instale dependências:
```
pip install -r requirements.txt
```
Execute:
```
python -m src.main
```

## Build para Windows (exe)
Após confirmar que roda localmente:
```
pip install pyinstaller
pyinstaller -F -w -n brainrot_game --add-data "assets:assets" src/main.py
```
Se usar PowerShell, ajustar aspas. Copie a pasta `assets` para o mesmo diretório do exe, mantendo hierarquia.
