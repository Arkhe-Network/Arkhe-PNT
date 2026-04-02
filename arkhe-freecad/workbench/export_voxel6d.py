import FreeCAD as App
import FreeCADGui as Gui
import json
import struct
import math

class ExportVoxel6DCommand:
    def GetResources(self):
        return {
            'Pixmap': ':/icons/export_6d.svg',
            'MenuText': 'Exportar Voxel6D',
            'ToolTip': 'Converte geometria para malha de fase e exporta .v6d'
        }
    
    def Activated(self):
        sel = Gui.Selection.getSelection()
        if not sel:
            App.Console.PrintError("Selecione um objeto para exportar.\n")
            return
        
        obj = sel[0]
        
        # Diálogo para salvar
        from PySide2 import QtWidgets
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            None, "Exportar Voxel6D", "", "Voxel6D JSON (*.v6d);;Voxel6D Binary (*.v6db)"
        )
        
        if not filename:
            return
            
        resolution = 1.0 # mm (Pode ser configurado no painel)
        
        # Extrai propriedades 6D (se existirem)
        mat = None
        if hasattr(obj, "Material6D"):
            mat = obj.Material6D
        elif hasattr(obj, "Group"):
            for child in obj.Group:
                if child.TypeId == "App::FeaturePython" and child.Proxy.Type == "Material6D":
                    mat = child
                    break
        
        # Valores padrão
        target_phase = 0.0
        elasticity = 70.0
        conductivity = 6.3e7
        mat_id = 1
        
        if mat:
            target_phase = mat.TargetPhase
            elasticity = mat.YoungModulus
            conductivity = mat.ElectricalConductivity
            mat_id = mat.MaterialType.index(mat.MaterialType[0]) + 1
            
        # Voxelização simples (Raycasting na BoundingBox)
        bb = obj.Shape.BoundBox
        voxels = []
        
        x_steps = int((bb.XMax - bb.XMin) / resolution)
        y_steps = int((bb.YMax - bb.YMin) / resolution)
        z_steps = int((bb.ZMax - bb.ZMin) / resolution)
        
        App.Console.PrintMessage(f"Voxelizando {x_steps}x{y_steps}x{z_steps}...\n")
        
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
                            "mat_id": mat_id,
                            "elasticity": elasticity,
                            "conductivity": conductivity,
                            "target_phase": target_phase
                        })
        
        # Exportação
        if filename.endswith(".v6db"):
            self.export_binary(filename, voxels)
        else:
            self.export_json(filename, voxels)
            
        App.Console.PrintMessage(f"Exportado {len(voxels)} voxels para {filename}\n")

    def export_json(self, filename, voxels):
        data = {
            "version": "1.0",
            "metadata": {
                "timestamp": "2026-03-25T00:00:00Z", # Idealmente dinâmico
                "source": "FreeCAD Arkhe Workbench"
            },
            "voxels": voxels
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def export_binary(self, filename, voxels):
        # Formato Binário Compacto (x, y, z, mat_id, E, C, phase)
        # fff i f f f
        with open(filename, 'wb') as f:
            f.write(b'V6DB') # Magic number
            f.write(struct.pack('<I', len(voxels))) # Contagem
            for v in voxels:
                f.write(struct.pack('<fffifff', 
                    v['x'], v['y'], v['z'], 
                    v['mat_id'], 
                    v['elasticity'], v['conductivity'], v['target_phase']
                ))

Gui.addCommand('Arkhe_ExportVoxel6D', ExportVoxel6DCommand())
