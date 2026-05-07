# Sobreviva ao Semestre

Um jogo arcade 2D estilo bullet-hell desenvolvido inteiramente com algoritmos de Computação Gráfica, utilizando apenas a função `set_pixel` do PyGame como primitiva gráfica.

## Sobre o Jogo

Você é um **aluno universitário** que precisa sobreviver à disciplina do temido **Professor Negresco**. Desvie dos projéteis (notas baixas!) e ataque com seus lápis até derrotar o boss!

O jogo é inspirado no gênero **bullet-hell** (estilo Touhou), com padrões de projéteis em espiral, anéis, cruzes e chuva caótica.

### Tela de Título

A tela de abertura apresenta o confronto **ALUNO vs NEGRESCO**, com:
- Aluno desenhado com polígonos (corpo, pernas, mochila, capelo) preenchidos por scanline e gradiente
- Boss renderizado com textura mapeada no polígono
- Animações de rotação, pulsação, caminhada e raios giratórios
- Decorações com circunferências, elipses e retas (Bresenham)

### Gameplay

- Área de jogo estilo Touhou (painel à esquerda) com HUD informativo à direita
- Câmera que segue o jogador com suavização (lerp)
- Sistema de zoom controlável (+/-, scroll do mouse)
- Minimap em tempo real mostrando a posição de todos os elementos
- Ataque automático direcionado pelo mouse (4 lápis em leque)
- Modo foco (Shift): velocidade reduzida e hitbox visível para desvios precisos
- 6 padrões de ataque do boss que se alternam ciclicamente

## Algoritmos de Computação Gráfica Implementados

Todos os algoritmos foram implementados do zero, sem uso de bibliotecas gráficas além do `set_pixel` (`surface.set_at`).

| Algoritmo | Arquivo | Descrição |
|---|---|---|
| Set Pixel | `graphics/primitives.py` | Operação fundamental com verificação de limites |
| Reta (Bresenham) | `graphics/primitives.py` | Rasterização de retas com aritmética inteira |
| Circunferência (Bresenham) | `graphics/primitives.py` | Simetria de 8 octantes + versão preenchida |
| Elipse (Bresenham) | `graphics/primitives.py` | Duas regiões, simetria de 4 quadrantes |
| Scanline Fill | `graphics/fill.py` | Preenchimento de polígonos por varredura |
| Scanline com Gradiente | `graphics/fill.py` | Interpolação bilinear de cores por vértice |
| Scanline com Textura | `graphics/fill.py` | Mapeamento UV com interpolação |
| Scanline com Alpha | `graphics/fill.py` | Textura com transparência (sprites) |
| Flood Fill | `graphics/fill.py` | Preenchimento por semente (4-conectado, iterativo) |
| Translação | `graphics/transform.py` | Matriz homogênea 3×3 |
| Escala | `graphics/transform.py` | Matriz homogênea 3×3 |
| Rotação | `graphics/transform.py` | Matriz homogênea 3×3 |
| Composição de Transformações | `graphics/transform.py` | Multiplicação de matrizes |
| Janela → Viewport | `graphics/transform.py` | Mapeamento mundo → tela |
| Cohen-Sutherland | `graphics/clipping.py` | Recorte de linhas com códigos de região |
| Fonte Bitmap | `graphics/text.py` | Caracteres 3×5 desenhados pixel a pixel |

## Estrutura do Projeto

```
trabalho-1-cg/
├── main.py                 # Ponto de entrada
├── assets/                 # Sprites e texturas
│   ├── negresco.png        # Sprite do boss
│   ├── lapis.png           # Sprite do projétil
├── game/                   # Lógica do jogo
│   ├── game.py             # Loop principal, colisões, ataques
│   ├── renderer.py         # Renderização (usa os algoritmos gráficos)
│   ├── entities.py         # Player, Boss, Projectile
│   ├── camera.py           # Sistema de câmera
│   ├── state.py            # Estados do jogo (título, jogando, etc.)
│   ├── config.py           # Configurações e formas dos personagens
│   ├── assets.py           # Carregamento de texturas para matrizes
│   └── powers.py           # Sistema de poderes (não utilizado atualmente)
├── graphics/               # Implementação dos algoritmos de CG
│   ├── primitives.py       # Set pixel, reta, círculo, elipse
│   ├── fill.py             # Scanline, gradiente, textura, flood fill
│   ├── transform.py        # Matrizes 2D, transformações, viewport
│   ├── clipping.py         # Cohen-Sutherland
│   └── text.py             # Fonte bitmap e utilitários
└── README.md
```

## Controles

| Tecla | Ação |
|---|---|
| W / A / S / D ou Setas | Mover o jogador |
| Shift (esquerdo ou direito) | Modo foco (lento + hitbox visível) |
| Mouse | Direção do ataque |
| Scroll do mouse ou +/- | Zoom in/out |
| ESC ou P | Pausar / Despausar |
| Enter ou Space | Selecionar opção no menu |

## Como Compilar e Executar

### Requisitos

- **Python** 3.8 ou superior

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/trabalho-1-cg.git
cd trabalho-1-cg
```

2. Crie e ative o ambiente virtual:

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o jogo:
```bash
python main.py
```

### Execução rápida (sem venv)

```bash
pip install pygame && python main.py
```

## Vídeo de Demonstração

[Link para o vídeo](INSERIR_LINK_AQUI)

## Funcionalidades Detalhadas

### Janela e Viewport
- **Viewport principal**: área de jogo (460×560 pixels) com transformação Window→Viewport
- **Minimap**: segunda viewport no HUD mostrando o mundo inteiro em escala reduzida
- **Translação**: câmera segue o jogador com interpolação suave
- **Escala (zoom)**: controlável de 0.5× a 3.0× via teclado ou scroll

### Recorte (Clipping)
- Grid da área de jogo recortado com Cohen-Sutherland
- Polígonos no minimap recortados para não sair da área
- Borda do mundo recortada quando visível com zoom

### Animações
- Boss rotaciona continuamente com escala pulsante
- Pernas do jogador simulam caminhada
- Raios giratórios ao redor do aluno na tela de título
- Texto do título oscila verticalmente
- Elipses decorativas pulsam ao redor do "VS"
- Projéteis se movem em padrões complexos (espirais, anéis, cruzes)

### Menu Interativo
- Tela de título com opções JOGAR / SAIR
- Navegação por teclado (setas ou WASD)
- Telas de pausa, game over e vitória com informações

## Equipe

- Pedro (e demais membros da equipe)

## Disciplina

Computação Gráfica — 2025.1
