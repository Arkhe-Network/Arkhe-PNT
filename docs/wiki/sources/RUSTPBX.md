# RustPBX: AI-Native Communication Infrastructure 🜏

A high-performance Software-Defined PBX built in Rust, designed as an AI-native communication platform for next-generation agentic orchestration. RustPBX externalizes call control via HTTP, WebSocket, and Webhooks, making AI a native participant in every telephonic event.

## 📡 Software-Defined Communication

RustPBX breaks traditional closed architectures by exposing three primary integration channels:

| Channel | Protocol | Purpose |
| :--- | :--- | :--- |
| **Policy Decision** | HTTP Router | Real-time routing decisions: AI-first, agent queue, or IVR. |
| **Real-time Control** | RWI (WebSocket) | In-call control: listen, whisper, barge, transfer, and PCM injection. |
| **Event Stream** | Webhook | Push CDR, queue status, and events to CRM/Atelier systems. |

## 🧠 AI-Native Architecture

The infrastructure supports seamless integration of voice-enabled agents:
- **Media Fabric:** RTP relay and NAT traversal with WebRTC bridging.
- **SenseVoice Integration:** Offline, post-call transcription for data-driven agent memory.
- **PCM Injection:** Direct AI-to-Call media streaming via RWI protocol.

## ⚙️ Core Capabilities
- **SIP Proxy:** Full stack supporting UDP/TCP/WS/TLS/WebRTC.
- **Queue/ACD:** Sequential or parallel agent ringing with priority scheduling.
- **SipFlow:** Unified SIP+RTP recording with hourly log rotation.

## 🔗 Original Source
[GitHub Repository: restsend/rustpbx](https://github.com/restsend/rustpbx)
