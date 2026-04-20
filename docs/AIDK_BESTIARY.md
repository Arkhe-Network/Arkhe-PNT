# AIDK Bestiary Specification (Anexo Y)
## Visual Metaphors for the Multiverse of Defense

---

**Classificação:** Público (Dev Portal)
**Objetivo:** Padronizar a aparência e o comportamento dos elementos interativos do jogo para garantir a correta tradução pela Muralha de Quartzo.

### 1. Princípios Fundamentais do Design Visual

1.  **Ambiguidade Deliberada:** Nenhum monstro deve ter um nome técnico no jogo. Um "Verme de Pedra" nunca é chamado de "SQL Injection". Ele é apenas um verme que corrói fundações. A tradução é responsabilidade exclusiva da Muralha.
2.  **Paleta de Cor Restrita (O Espectro do Caos):**
    - **Azul/Prata:** Estruturas saudáveis, dados íntegros, cristais puros.
    - **Púrpura/Néon:** Vazamento de dados, exposição de informação (`SHADOW_LEAK`).
    - **Vermelho/Laranja (Opaco):** Falha de integridade, corrupção de dados, underflow (`STONE_WORM`).
    - **Cinza/Estático:** Negação de serviço, latência, sistemas sobrecarregados (`VOID_SWARM`).
3.  **Topologia do Movimento:**
    - **Rastejante/Reticulado:** Ataques de injeção e persistência.
    - **Expansivo/Gasoso:** Vazamento e exfiltração.
    - **Clonagem/Espelhamento:** Falhas de autenticação e usurpação de identidade.

### 2. O Bestiário Oficial (Assets 3D/2D)

| Nome do Monstro (In-Game) | Vulnerabilidade Mapeada (CWE) | Aparência (Diretrizes de Arte) | Comportamento (Diretrizes de Animação) |
| :--- | :--- | :--- | :--- |
| **Verme de Pedra** | **CWE-89 (SQL Injection)** | Corpo segmentado de rocha negra com veios vermelhos opacos. Brilho interno fraco. | Move-se **dentro** de paredes e pisos, deixando um rastro de textura rachada. Só emerge para "morder" estruturas. |
| **Sombra Vazante** | **CWE-200 (Information Exposure)** | Forma humanoide vaga, composta de **fumaça púrpura** que se dissipa nas bordas. Olhos são vazios absolutos. | Flutua lentamente, ignorando colisões. Quando "ataca", ela atravessa o jogador, causando distorção visual na tela. |
| **Doppelgänger** | **CWE-287 (Authentication Bypass)** | Inicialmente invisível. Assume a forma do jogador ou de um NPC aliado, mas com **olhos de fogo púrpura** e textura levemente tremida. | Tenta se passar por aliado. Quando o jogador se aproxima muito, emite um grito distorcido e ataca com as mesmas animações do jogador. |
| **Praga de Gafanhotos** | **CWE-400 (Resource Exhaustion / DoS)** | Nuvem de milhares de pequenos fragmentos de **quartzo negro** que zumbem como estática. | Causa lentidão no movimento do jogador (simulando lag). Não causa dano direto, mas impede ações rápidas. |
| **Cristal Invertido** | **CWE-754 (Improper Check)** | Um cristal que, em vez de emitir luz, **suga a luz** ao redor, criando uma aura de escuridão. | Imóvel. Se o jogador interagir com ele sem o feitiço/ferramenta correta, ele "drena" a barra de energia/magia. |

### 3. Diretrizes para Mundos Voxelados (Minecraft/Roblox)

Para jogos baseados em blocos, as texturas devem seguir um padrão de **Ruído de Perlin** para simular a "corrupção" de dados.

- **Bloco Corrompido (Verme):** Textura de `stone.png` com overlay de `magma.png` em baixa opacidade e partículas de `portal`.
- **Bloco de Vazamento (Sombra):** Bloco de `vidro` com interior de `fumaça` (partículas) que escapam para cima.
- **Entidade Doppelgänger:** Um `Player Head` com olhos de `Enderman` que fica parado até o jogador se aproximar.

### 4. Sons e Áudio Espacial (Imersão sem Informação)

- **Verme de Pedra:** Som de **rocha rangendo** e **eco abafado**.
- **Sombra Vazante:** **Sussurros ininteligíveis** e **vento agudo**.
- **Doppelgänger:** O som dos **passos do jogador**, mas **desincronizado** e com **reverb invertido**.
