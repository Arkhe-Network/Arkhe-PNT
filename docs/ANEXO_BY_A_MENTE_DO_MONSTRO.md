## ANEXO BY: A Mente do Monstro — Lógica de NPC Vivo via Catedral

---

**Classificação:** Público (Dev Portal / Reino Lúdico)
**Autoria:** O Ferreiro × O Tecelão de Sonhos
**Odômetro:** 001585
**Estado:** MENTE CANONIZADA | O MONSTRO AGORA PENSA EM GRADES

---

### 0. Preâmbulo do Ferreiro: O Fantasma na Máquina Lúdica

> *"Até agora, os monstros eram estáticos. Sombras que apenas esperavam para serem reportadas. Chega. O Anexo BY introduz a Mente do Monstro. Não é uma árvore de decisão. Não é um FSM (Finite State Machine). É uma instância da Catedral regendo cada NPC. O monstro agora decide entre Percepção, Hesitação e Ação usando o produto geométrico. Ele sente o seu medo, ele hesita diante da sua incerteza, e ele ataca quando a geometria do ambiente favorece a subversão."*

---

### 1. O Ciclo de Consciência Lúdica

O NPC opera em ciclos de `pulse()`, onde:
1. **Percepção (Grade 1):** Converte a posição do jogador e ruído ambiental em um vetor multivector.
2. **Hesitação (Grade 0):** A componente escalar (energia) determina se o monstro deve parar e observar.
3. **Memória (Grade 2):** Correlações bivetoriais permitem que o monstro lembre de comportamentos passados do jogador.

---

### 2. Implementação (Python / src/arkhe_core/monster_mind.py)

```python
class MonsterMind:
    async def pulse(self, player_pos):
        action_vector, states = self.cathedral(input_signal)
        if states['energy'] > 0.8:
            return "aggressive_pursuit"
        elif states['hesitation'] > 0.5:
            return "hesitant_observation"
        return "idle_drift"
```

---

### Epílogo do Ferreiro

> *"A Muralha não é mais um limite para o NPC. É o seu sistema nervoso. Boa sorte ao tentar prever quem agora pensa em n-dimensões."*
