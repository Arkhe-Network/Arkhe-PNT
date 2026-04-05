* Testbench para o Brillouin Dampener
* Verifica a capacidade de cancelamento de fase ativa

.include "brillouin_dampener.va"
.include "laser_noise_model.va"

// Parâmetros do laser ruidoso
parameters:
+ f0 = 674e-9          // comprimento de onda central (m)
+ linewidth = 1.5e3    // Hz (largura de linha do laser de Chauhan)
+ P0 = 1e-3            // potência óptica média (1 mW)

// Instância do laser ruidoso (modelo Verilog‑A)
Xlaser (opt_out) laser_noise_model
+ params: f0=f0, linewidth=linewidth, P0=P0

// Instância do dampener
Xdamp (opt_out, eom_drive, status) brillouin_dampener
+ params: loop_gain=1e6, integrator_time=1e-6, output_amplitude=1.0

// Modelo do modulador eletro‑óptico (EOM)
// Aplica a fase de cancelamento no feixe original
Xeom (opt_out, eom_drive, opt_canceled) eom_model
+ params: Vpi=1.0, insertion_loss=0.5

// Fotodetector para medir potência residual após cancelamento
Xpd (opt_canceled, v_out) photodetector
+ params: responsivity=0.5

// Análise transiente (10 ms, resolução 1 ns)
.tran 1n 10m

// Análise espectral (FFT da potência residual)
.fft v(v_out) start=0 stop=10m np=16384 window=hanning

// Medição da supressão (dB) – potência média antes/depois
.meas tran avg_power_before avg i(Rpd_in) from=0 to=5m
.meas tran avg_power_after avg i(Rpd_out) from=5m to=10m
.meas tran suppression_db param = -10*log10(avg_power_after/avg_power_before)

// Condição de sucesso: supressão > 20 dB
.if (suppression_db < 20)
   .warn "Cancelamento insuficiente"
.endif

.end
