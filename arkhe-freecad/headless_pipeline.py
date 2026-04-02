import FreeCAD as App
import Part
import Mesh
import json
import argparse
import sys
import os
import math

def convert_to_voxel6d(input_file, output_file, resolution=1.0, target_phase=0.0):
    """
    Converte um arquivo CAD (STEP, IGES, BREP) para o formato Voxel6D JSON
    em modo headless.
    """
    print(f"Iniciando conversão de {input_file} para {output_file}...")
    
    # Cria um documento temporário
    doc = App.newDocument("HeadlessConversion")
    
    # Importa o arquivo
    try:
        if input_file.lower().endswith(".step") or input_file.lower().endswith(".stp"):
            import ImportGui
            ImportGui.insert(input_file, doc.Name)
        elif input_file.lower().endswith(".iges") or input_file.lower().endswith(".igs"):
            import IgesGui
            IgesGui.insert(input_file, doc.Name)
        elif input_file.lower().endswith(".brep"):
            import Part
            shape = Part.Shape()
            shape.read(input_file)
            obj = doc.addObject("Part::Feature", "ImportedShape")
            obj.Shape = shape
        else:
            print("Formato de arquivo não suportado.")
            return False
    except Exception as e:
         print(f"Erro ao importar arquivo: {e}")
         return False

    # Encontra o objeto principal (assumindo que é o primeiro)
    if not doc.Objects:
        print("Nenhum objeto importado.")
        return False
        
    obj = doc.Objects[0]
    
    # Voxelização (Raycasting simples)
    if not hasattr(obj, "Shape"):
        print("Objeto não possui geometria (Shape).")
        return False
        
    bb = obj.Shape.BoundBox
    voxels = []
    
    x_steps = int((bb.XMax - bb.XMin) / resolution)
    y_steps = int((bb.YMax - bb.YMin) / resolution)
    z_steps = int((bb.ZMax - bb.ZMin) / resolution)
    
    print(f"Voxelizando {x_steps}x{y_steps}x{z_steps} com resolução {resolution}mm...")
    
    for i in range(x_steps):
        x = bb.XMin + i * resolution + resolution/2
        for j in range(y_steps):
            y = bb.YMin + j * resolution + resolution/2
            for k in range(z_steps):
                z = bb.ZMin + k * resolution + resolution/2
                
                # Verifica se o ponto está dentro do sólido
                if obj.Shape.isInside(App.Vector(x, y, z), resolution/10, True):
                    voxels.append({
                        "x": x, "y": y, "z": z,
                        "mat_id": 1, # Padrão
                        "elasticity": 70.0, # GPa (Alumínio genérico)
                        "conductivity": 3.5e7, # S/m
                        "target_phase": target_phase
                    })
    
    # Exportação JSON
    data = {
        "version": "1.0",
        "metadata": {
            "source": "FreeCAD Headless Pipeline",
            "original_file": os.path.basename(input_file)
        },
        "voxels": voxels
    }
    
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exportado com sucesso: {len(voxels)} voxels para {output_file}")
        return True
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conversor Headless FreeCAD para Voxel6D")
    parser.add_argument("input", help="Arquivo CAD de entrada (STEP, IGES, BREP)")
    parser.add_argument("output", help="Arquivo Voxel6D JSON de saída")
    parser.add_argument("--res", type=float, default=1.0, help="Resolução do Voxel em mm")
    parser.add_argument("--phase", type=float, default=0.0, help="Fase Alvo (radianos)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Erro: Arquivo de entrada não encontrado: {args.input}")
        sys.exit(1)
        
    success = convert_to_voxel6d(args.input, args.output, args.res, args.phase)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
