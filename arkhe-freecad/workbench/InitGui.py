import FreeCAD as App
import FreeCADGui as Gui
import json
import struct
import math
import os
import sys

# Adiciona o diretório atual ao sys.path para importações relativas
dir_path = os.path.dirname(os.path.realpath(__file__))
if dir_path not in sys.path:
    sys.path.append(dir_path)

class ArkheWorkbench(Gui.Workbench):
    MenuText = "Arkhe 6D"
    ToolTip = "Workbench para manufatura quântica e Voxel6D"
    Icon = ":/icons/arkhe_logo.svg" # Precisa de um arquivo de recurso .qrc compilado

    def Initialize(self):
        # Importa os comandos
        import material_properties
        import export_voxel6d

        # Adiciona os comandos à barra de ferramentas e menu
        self.appendToolbar("Arkhe Tools", ["Arkhe_SetMaterial6D", "Arkhe_ExportVoxel6D"])
        self.appendMenu("Arkhe", ["Arkhe_SetMaterial6D", "Arkhe_ExportVoxel6D"])

    def Activated(self):
        # Executado quando o workbench é ativado
        App.Console.PrintMessage("Arkhe Workbench Ativado!\n")

    def Deactivated(self):
        # Executado quando o workbench é desativado
        App.Console.PrintMessage("Arkhe Workbench Desativado.\n")

Gui.addWorkbench(ArkheWorkbench())
