import FreeCAD as App

class Material6D:
    """
    Objeto FeaturePython que armazena propriedades quânticas
    no documento FreeCAD.
    """
    
    def __init__(self, obj):
        # Propriedades Físicas
        obj.addProperty("App::PropertyFloat", "YoungModulus", 
                       "Arkhe6D", "Módulo de Young (GPa)").YoungModulus = 70.0
        obj.addProperty("App::PropertyFloat", "PoissonRatio", 
                       "Arkhe6D", "Razão de Poisson").PoissonRatio = 0.33
        obj.addProperty("App::PropertyFloat", "ElectricalConductivity", 
                       "Arkhe6D", "Condutividade Elétrica (S/m)").ElectricalConductivity = 6.3e7
        
        # Propriedades de Fase (Quânticas)
        obj.addProperty("App::PropertyFloat", "TargetPhase", 
                       "Arkhe6D", "Fase Alvo θ (rad)").TargetPhase = 0.0
        obj.addProperty("App::PropertyFloat", "CoherenceTolerance", 
                       "Arkhe6D", "Tolerância Ω'").CoherenceTolerance = 0.95
        obj.addProperty("App::PropertyEnumeration", "MaterialType", 
                       "Arkhe6D", "Tipo de Material")
        obj.MaterialType = ["STRUCTURAL", "CONDUCTOR", "SENSOR", "HYBRID_6D"]
        
        # Metadados
        obj.addProperty("App::PropertyString", "PCode", 
                       "Arkhe6D", "Código P de Referência").PCode = "DEFAULT_001"
        
        obj.Proxy = self
        self.Type = "Material6D"
    
    def execute(self, obj):
        # Recalcula quando propriedades mudam
        pass
    
    def onChanged(self, obj, prop):
        # Validações
        if prop == "TargetPhase":
            # Normaliza para [0, 2π]
            while obj.TargetPhase < 0:
                obj.TargetPhase += 6.28318530718
            while obj.TargetPhase > 6.28318530718:
                obj.TargetPhase -= 6.28318530718


class ViewProviderMaterial6D:
    def __init__(self, vobj):
        vobj.Proxy = self
    
    def getIcon(self):
        return ":/icons/material_6d.svg"
    
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object


def createMaterial6D():
    """Factory function para criar Material6D"""
    doc = App.ActiveDocument or App.newDocument()
    obj = doc.addObject("App::FeaturePython", "Material6D")
    Material6D(obj)
    ViewProviderMaterial6D(obj.ViewObject)
    doc.recompute()
    return obj


# Comando para GUI
class SetMaterial6DCommand:
    def GetResources(self):
        return {
            'Pixmap': ':/icons/material_6d.svg',
            'MenuText': 'Definir Propriedades 6D',
            'ToolTip': 'Atribui elasticidade, condutividade e fase ao objeto'
        }
    
    def Activated(self):
        import FreeCADGui as Gui
        sel = Gui.Selection.getSelection()
        if not sel:
            return
        
        # Cria ou edita Material6D para o objeto selecionado
        obj = sel[0]
        if not hasattr(obj, "Material6D"):
            mat = createMaterial6D()
            # Vincula ao objeto (via grupo ou referência)
            if hasattr(obj, "addObject"):
                obj.addObject(mat)
        
        # Abre painel de tarefas (simplificado)
        Gui.Control.showDialog(Material6DTaskPanel(obj))
    
    def IsActive(self):
        import FreeCADGui as Gui
        return len(Gui.Selection.getSelection()) > 0


class Material6DTaskPanel:
    def __init__(self, obj):
        self.obj = obj
        from PySide2 import QtWidgets
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.form)
        
        # Widgets para edição
        self.phase_spin = QtWidgets.QDoubleSpinBox()
        self.phase_spin.setRange(0, 6.28)
        self.phase_spin.setDecimals(4)
        if hasattr(obj, "TargetPhase"):
            self.phase_spin.setValue(obj.TargetPhase)
        
        layout.addRow("Fase Alvo (rad):", self.phase_spin)
    
    def accept(self):
        if hasattr(self.obj, "TargetPhase"):
            self.obj.TargetPhase = self.phase_spin.value()
        return True

import FreeCADGui as Gui
Gui.addCommand('Arkhe_SetMaterial6D', SetMaterial6DCommand())
