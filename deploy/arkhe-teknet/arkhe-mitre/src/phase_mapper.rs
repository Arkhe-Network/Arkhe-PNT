use crate::ingestor::AgentSkill;
use labyrinth_rs::eisenstein::Eisenstein;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

pub struct MitrePhaseMapper {
    /// Mapeia o nome da skill para uma coordenada na Espiral de Sacks
    pub skill_to_eisenstein: HashMap<String, Eisenstein>,
}

impl MitrePhaseMapper {
    pub fn new() -> Self {
        Self {
            skill_to_eisenstein: HashMap::new(),
        }
    }

    /// Converte uma skill do MITRE ATT&CK em uma coordenada de fase
    pub fn map_skill_to_phase(&mut self, skill: &AgentSkill) -> Eisenstein {
        // Usa um hash do nome da skill e das tags para determinar a posição na espiral
        let mut hasher = DefaultHasher::new();
        skill.name.hash(&mut hasher);
        for tag in &skill.tags {
            tag.hash(&mut hasher);
        }
        let hash_val = hasher.finish();

        // Mapeia o hash para coordenadas (a, b) na rede de Eisenstein
        // Isso distribui as 734 skills pela topologia da Teknet
        let a = (hash_val % 100) as i64 - 50;
        let b = ((hash_val / 100) % 100) as i64 - 50;

        let coord = Eisenstein::new(a, b);
        self.skill_to_eisenstein.insert(skill.name.clone(), coord.clone());
        
        coord
    }

    pub fn map_all(&mut self, skills: &[AgentSkill]) {
        for skill in skills {
            self.map_skill_to_phase(skill);
        }
    }
}
