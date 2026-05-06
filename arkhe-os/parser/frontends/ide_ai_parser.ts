import { LFIRGraph, LFIRNode, LFIRNodeType, ParseResult } from '../lfir';

export enum IDETool {
    VSCODE = 'vscode',
    CURSOR = 'cursor',
    ANTIGRAVITY = 'antigravity',
    OPEN_CODE = 'open_code'
}

export interface DevEvent {
    tool: IDETool;
    event_type: string;
    file_path: string;
    content_snippet?: string;
    timestamp: number;
    session_id: string;
    metadata?: Record<string, any>;
}

export interface PrivacyConfig {
    redact_content: boolean;
    hash_file_paths: boolean;
}

export class IDEAndAIParser {
    private privacyConfig: PrivacyConfig;

    constructor(privacyConfig: PrivacyConfig = { redact_content: true, hash_file_paths: false }) {
        this.privacyConfig = privacyConfig;
    }

    public parse(eventsJson: string, namespace: string): ParseResult {
        const startTime = Date.now();
        let events: DevEvent[] = [];

        try {
            events = JSON.parse(eventsJson);
        } catch (e) {
            return {
                success: false,
                graph: null,
                errors: [{ code: 'PARSE_ERROR', message: 'Invalid JSON payload', severity: 'fatal' }],
                warnings: [],
                metrics: { parseTimeMs: Date.now() - startTime, nodesCreated: 0, edgesCreated: 0, maxDepth: 0, coherenceScore: 0 }
            };
        }

        const graph = new LFIRGraph();
        let coherenceNumerator = 0;
        let coherenceDenominator = 0;

        let previousNodeId: string | null = null;

        // Ensure events are sorted chronologically
        events.sort((a, b) => a.timestamp - b.timestamp);

        const now = Date.now();

        for (const event of events) {
            const nodeId = `event_${event.timestamp}_${Math.random().toString(36).substring(7)}`;

            // Map event to valid LFIRNodeType
            let type = LFIRNodeType.Operation;
            if (event.event_type === 'save' || event.event_type === 'edit') type = LFIRNodeType.Operation;
            else if (event.event_type === 'completion_accept' || event.event_type === 'completion_reject') type = LFIRNodeType.Metadata;

            const processedEvent = this.applyPrivacyConfig(event);

            const node = new LFIRNode(nodeId, type, 'DevEvent');
            node.attributes = {
                event_type: processedEvent.event_type,
                file_path: processedEvent.file_path,
                timestamp: processedEvent.timestamp,
                tool: processedEvent.tool,
                content: processedEvent.content_snippet,
                ...processedEvent.metadata
            };

            const eventCoherence = this.calculateEventCoherence(processedEvent);
            node.attributes['event_coherence'] = eventCoherence;

            if (eventCoherence > 0) {
                // Decaimento temporal: eventos mais antigos pesam menos (ex: meia-vida de 1 hora)
                const ageSec = (now - processedEvent.timestamp) / 1000;
                const decayWeight = Math.exp(-ageSec / 3600);

                coherenceNumerator += eventCoherence * decayWeight;
                coherenceDenominator += decayWeight;
            }

            graph.addNode(node);

            if (previousNodeId) {
                graph.link(previousNodeId, nodeId);
            }
            previousNodeId = nodeId;
        }

        const sessionCoherence = coherenceDenominator > 0 ? coherenceNumerator / coherenceDenominator : 0;

        // Add session coherence to the first node (if exists) or a root node
        if (graph.nodes.length > 0) {
            graph.nodes[0].attributes['coherence_score'] = sessionCoherence;
        }

        return {
            success: true,
            graph,
            errors: [],
            warnings: [],
            metrics: {
                parseTimeMs: Date.now() - startTime,
                nodesCreated: graph.nodes.length,
                edgesCreated: Math.max(0, graph.nodes.length - 1),
                maxDepth: graph.nodes.length, // simple linear sequence
                coherenceScore: sessionCoherence
            }
        };
    }

    private applyPrivacyConfig(event: DevEvent): DevEvent {
        let newEvent = { ...event };

        if (this.privacyConfig.redact_content && newEvent.content_snippet) {
            // Simple regex for secrets/tokens redaction MVP
            newEvent.content_snippet = newEvent.content_snippet.replace(/(bearer\s+|token\s*=\s*|key\s*=\s*)['"]?([a-zA-Z0-9_\-\.]{10,})['"]?/gi, '$1"[REDACTED]"');
            newEvent.content_snippet = newEvent.content_snippet.replace(/(password\s*=\s*)['"]?([^'"\s]+)['"]?/gi, '$1"[REDACTED]"');
        }
        if (this.privacyConfig.hash_file_paths) {
             // Simple pseudo-hash
             let hash = 0;
             for (let i = 0; i < newEvent.file_path.length; i++) {
                 hash = Math.imul(31, hash) + newEvent.file_path.charCodeAt(i) | 0;
             }
             newEvent.file_path = `hash_${Math.abs(hash)}`;
        }
        return newEvent;
    }

    private calculateEventCoherence(event: DevEvent): number {
        switch (event.event_type) {
            case 'save': return 0.9;
            case 'completion_accept': return 0.8;
            case 'completion_reject': return 0.2;
            case 'edit': return 0.5;
            case 'diagnostic_fix': return 0.95;
            case 'diagnostic_error': return 0.1;
            case 'agent_action': return 0.7;
            default: return 0.5;
        }
    }
}
