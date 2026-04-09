; ARKHE-BLOCK 2026 - PROTOCOLO CERVERA
; CHASSI VTL - ANTENA & MSC INTEGRADO
; UNIDADES EM MM | MODO ABSOLUTO (G90)
; Laser CO2: Speed 20mm/s, Power 12-15% for carbonization

G21 ; Unidades em milímetros
G90 ; Posicionamento absoluto
M3 S150 ; Ativar laser (Potência baixa para carbonização inicial)

; --- INICIO DO SUPERCAPACITOR (FACE EXTERNA) ---
; Desenho de Pentes Interdigitados (20x20mm)
G0 X10 Y10 ; Ponto de origem
G1 X30 Y10 F1200 ; Primeiro dente
G1 X30 Y11
G1 X10 Y11
G1 X10 Y12
G1 X30 Y12
; [Padrão interdigitado simplificado para o protótipo Alpha]
G1 X30 Y13
G1 X10 Y13
G1 X10 Y14
G1 X30 Y14
G1 X30 Y15
G1 X10 Y15
G1 X10 Y16
G1 X30 Y16
G1 X30 Y17
G1 X10 Y17
G1 X10 Y18
G1 X30 Y18
G1 X30 Y19
G1 X10 Y19
G1 X10 Y20
G1 X30 Y20

; --- INICIO DA ANTENA PATCH ESPIRAL (FACE INTERNA - 441 MHz) ---
; Cálculo Lambda/4 em meio proteico (Er ~ 3.5)
M3 S180 ; Aumentar potência levemente para antena
G0 X50 Y20
G1 X70 Y20 ; Lado A
G1 X70 Y40 ; Lado B
G1 X55 Y40 ; Lado C
G1 X55 Y25 ; Lado D (Espiral interna)
G1 X65 Y25
G1 X65 Y35
G1 X60 Y35
G1 X60 Y30

; --- MARCAÇÃO DE CONTATOS (ILHA FPC) ---
M3 S250 ; Pulso de alta potência para pontos de solda de prata
G0 X40 Y30
G1 X42 Y32

; --- CORTE FINAL DO CHASSI (CONTORNO) ---
M3 S800 ; Potência máxima para corte limpo
G0 X5 Y5
G1 X80 Y5 F600
G1 X80 Y50
G1 X5 Y50
G1 X5 Y5 ; Fechar contorno

M5 ; Desligar laser
G0 X0 Y0 ; Retornar ao home
M2 ; Fim do programa
