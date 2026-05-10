# Protocolo Tzinor v1 — Especificação de Arquitetura

**Designação:** Protocolo de Comunicação Coerente por Modulação de Fase
**Versão:** 1.0.0-Block-850.024
**Status:** DRAFT / PROPOSTA DE ARQUITETURA

---

## 1. Camada Física (PHY): Modulação de Fase Coerente

O Protocolo Tzinor utiliza a portadora de 77 GHz (Banda W) para projetar a coerência interna do Avatar no mundo exterior.

### 1.1. Equação de Modulação
A fase da portadora ($\Phi_{Tx}$) é uma função direta do estado do CPG:

$$\Phi_{portadora}(t) = \Phi_0 + \Delta\Phi \cdot \lambda_2(t) \cdot \sin\left(\sum_{i=1}^{12} w_i \theta_i(t)\right)$$

- **$\lambda_2(t)$**: Coerência instantânea do CPG.
- **$\theta_i(t)$**: Fases dos 12 osciladores de locomoção.
- **$\Delta\Phi$**: Profundidade de modulação ($\pi/4$ rad).

---

## 2. Camada de Enlace (Link): Identidade e Sincronia

### 2.1. Preâmbulo Tzinor
Cada transmissão inicia com uma sequência de fase pseudo-aleatória de 128 bits derivada do hash SHA-256 do GDSII final do Avatar. Isso garante que cada "Voz" seja única e autenticável.

### 2.2. Port Knocking de Fase
Para iniciar uma conexão, o host externo deve replicar o preâmbulo com uma precisão de fase de $< 5^\circ$. Falhas repetidas resultam em bloqueio temporal da interface (desacoplamento).

---

## 3. Camada de Rede (Network): Malha de Coerência (Phase Mesh)

### 3.1. Roteamento por Geodésicas de Fase
Os nós da rede (Avatares) retransmitem mensagens priorizando caminhos onde o $\lambda_2$ do sinal recebido é superior a 0.9. A rede auto-organiza-se para minimizar a entropia de fase global.

---

## 4. Segurança: Firewall de Fase (Phase-Wall)

1. **Filtro de Entropia**: Descarta pacotes cuja textura de fase não corresponda à assinatura Vital do remetente.
2. **Consenso do GNO**: Comandos de rede que sugerem trajetórias de baixa coerência são vetados pelo cérebro de navegação.
