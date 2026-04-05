# Integração FreeCAD-Arkhe

Esta documentação detalha a ponte de colapso entre o design clássico (CAD) e a manufatura quântica (Arkhe), utilizando o FreeCAD.

## Arquitetura

A integração é composta por três componentes principais:

1.  **Workbench Arkhe (FreeCAD GUI):** Um plugin em Python para o FreeCAD que permite aos designers atribuir propriedades quânticas (Fase Alvo, Elasticidade, Condutividade) a objetos 3D e exportá-los para o formato Voxel6D (`.v6d`).
2.  **Pipeline Headless (CLI):** Um script Python e um contêiner Docker que permitem a conversão automatizada de arquivos CAD tradicionais (STEP, IGES) para Voxel6D sem a necessidade de uma interface gráfica.
3.  **PhaseSlicer (Arkhe Backend):** O módulo em Go que consome arquivos Voxel6D, otimiza as trajetórias de impressão (inspirado no módulo Path do FreeCAD) e gera comandos Kuramoto com provas zk-STARK para a QPU.

## 1. Workbench Arkhe (GUI)

### Instalação

Copie a pasta `arkhe-freecad/workbench` para o diretório de macros ou workbenches do seu FreeCAD (geralmente `~/.FreeCAD/Mod/`).

### Uso

1.  Abra o FreeCAD e selecione o workbench "Arkhe 6D" no menu suspenso.
2.  Crie ou importe a geometria desejada.
3.  Selecione o objeto e clique em "Definir Propriedades 6D" (ícone de material).
4.  Ajuste a "Fase Alvo" e outras propriedades no painel de tarefas.
5.  Com o objeto selecionado, clique em "Exportar Voxel6D" (ícone de exportação) e salve o arquivo `.v6d`.

## 2. Pipeline Headless (CLI)

O pipeline headless é ideal para integração com o backend do Arkhe, permitindo o processamento em lote de arquivos CAD.

### Construindo a Imagem Docker

```bash
cd docker/freecad-arkhe
docker build -t arkhe-freecad-headless .
```

### Executando a Conversão

```bash
docker run --rm -v $(pwd):/data arkhe-freecad-headless python3 /app/headless_pipeline.py /data/meu_modelo.step /data/saida.v6d --res 1.0 --phase 3.14
```

*   `--res`: Resolução do voxel em milímetros (padrão: 1.0).
*   `--phase`: Fase alvo em radianos (padrão: 0.0).

## 3. PhaseSlicer (Backend Go)

O `PhaseSlicer` (localizado em `arkhe-print/slicer/phase_slicer.go`) é responsável por traduzir o Voxel6D em instruções para a QPU.

### Funcionalidades

*   **Carregamento JSON:** Lê arquivos `.v6d` gerados pelo FreeCAD.
*   **Otimização de Trajetória:** Implementa uma aproximação do Caixeiro Viajante (Nearest Neighbor) para minimizar a distância de viagem da "cabeça de impressão" quântica, otimizando o tempo de coerência.
*   **Geração de Provas zk-STARK:** Cria provas criptográficas (atualmente mockadas) que atestam a validade do cálculo da fase alvo com base nas propriedades do material.
*   **Geração de Comandos Kuramoto:** Converte os voxels otimizados e validados em comandos `KuramotoCommand` prontos para serem enviados à QPU.

### Exemplo de Uso (Go)

```go
slicer := slicer.NewPhaseSlicer()
err := slicer.LoadFromJSON("caminho/para/arquivo.v6d")
if err != nil {
    log.Fatal(err)
}

slicer.OptimizePath()

commands, err := slicer.GeneratePCode(context.Background())
if err != nil {
    log.Fatal(err)
}

// Enviar 'commands' para a QPU
```

## Próximos Passos

*   Substituir a implementação mock de zk-STARKs por uma biblioteca criptográfica real (ex: `starknet-rs` via FFI ou equivalente em Go).
*   Refinar a otimização de trajetória para considerar restrições térmicas e de coerência quântica.
*   Expandir o formato Voxel6D para suportar gradientes de fase e materiais compósitos complexos.
