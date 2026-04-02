import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

class FidelityJumpVisualizer:
    """
    Simula a fidelidade de um par EPR ao longo do tempo, com:
    - Perda de pacotes (tempestade solar)
    - Reconstrução via filtro de Kalman (linha azul tracejada)
    - Recepção do super‑pacote (linha vermelha vertical) e restauração da fidelidade
    """
    def __init__(self, duration=100, loss_rate=0.3, storm_interval=(30, 70)):
        self.duration = duration
        self.loss_rate = loss_rate
        self.storm_start, self.storm_end = storm_interval
        self.time = np.arange(duration)
        self.true_fidelity = self._ideal_fidelity()
        self.measured_fidelity = self._apply_loss_and_noise()
        self.reconstructed_fidelity = self._kalman_reconstruction()
        self.super_packet_time = self.storm_end + 5  # 5 unidades após o fim da tempestade
        self.final_fidelity = self._apply_super_packet()

    def _ideal_fidelity(self):
        """Fidelidade perfeita (1.0) sem tempestade."""
        return np.ones(self.duration)

    def _apply_loss_and_noise(self):
        """Simula perda de pacotes e ruído durante a tempestade."""
        fid = self.true_fidelity.copy()
        for t in range(self.duration):
            if self.storm_start <= t <= self.storm_end:
                # Dentro da tempestade: perda de pacotes e ruído
                if np.random.rand() < self.loss_rate:
                    fid[t] = 0.0  # pacote perdido
                else:
                    # Ruído gaussiano reduz fidelidade
                    noise = np.random.normal(0, 0.15)
                    fid[t] = max(0.0, min(1.0, fid[t] - noise))
            else:
                # Fora da tempestade: pequena degradação natural
                fid[t] = max(0.0, min(1.0, fid[t] - 0.01 * np.random.rand()))
        return fid

    def _kalman_reconstruction(self):
        """Aplica filtro de Kalman para preencher lacunas."""
        rec = self.measured_fidelity.copy()
        # Interpolação linear simples + suavização (simula Kalman)
        missing = np.where(rec == 0)[0]
        if len(missing) > 0:
            # Preenche lacunas com média móvel
            for t in missing:
                if t > 0 and t < self.duration-1:
                    rec[t] = (rec[t-1] + rec[t+1]) / 2
        # Suavização
        rec = savgol_filter(rec, window_length=11, polyorder=3)
        return np.clip(rec, 0, 1)

    def _apply_super_packet(self):
        """Restaura a fidelidade após receber o super‑pacote."""
        final = self.reconstructed_fidelity.copy()
        # Após o super‑pacote, a fidelidade retorna ao valor ideal
        final[self.super_packet_time:] = 1.0
        return final

    def plot(self, save_path="fidelity_jump.png"):
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(self.time, self.true_fidelity, 'k--', linewidth=1, alpha=0.5, label='Fidelidade ideal')
        ax.scatter(self.time, self.measured_fidelity, s=10, c='red', alpha=0.6, label='Medições (perdidas/ruidosas)')
        ax.plot(self.time, self.reconstructed_fidelity, 'b-', linewidth=2, label='Reconstrução Kalman (estimada)')
        ax.plot(self.time, self.final_fidelity, 'g-', linewidth=2, label='Pós Super‑Pacote')
        ax.axvline(x=self.storm_start, color='orange', linestyle=':', label='Início tempestade')
        ax.axvline(x=self.storm_end, color='orange', linestyle=':', label='Fim tempestade')
        ax.axvline(x=self.super_packet_time, color='magenta', linewidth=2, label='Super‑pacote recebido')

        # Destacar o salto de fidelidade
        y_before = self.final_fidelity[self.super_packet_time - 1]
        y_after = self.final_fidelity[self.super_packet_time]
        ax.annotate(f'Salto de Fidelidade: {y_before:.2f} → {y_after:.2f}',
                    xy=(self.super_packet_time, y_after),
                    xytext=(self.super_packet_time+5, y_after-0.2),
                    arrowprops=dict(arrowstyle='->', color='magenta'),
                    fontsize=10, color='magenta')

        ax.set_xlabel('Tempo (unidades arbitrárias)')
        ax.set_ylabel('Fidelidade do Estado EPR')
        ax.set_title('Salto de Fidelidade Proporcionado pelo Super‑Pacote Recursivo')
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")

if __name__ == "__main__":
    viz = FidelityJumpVisualizer(duration=100, loss_rate=0.4, storm_interval=(30, 70))
    viz.plot()
