# Chrome DevTools MCP & Arkhe(n) Monorepo

[![npm chrome-devtools-mcp package](https://img.shields.io/npm/v/chrome-devtools-mcp.svg)](https://npmjs.org/package/chrome-devtools-mcp)

This repository is a monorepo containing the **Chrome DevTools MCP** server and the **Arkhe(n) Bio-Quantum Cathedral** framework. It bridges standard web automation with experimental simulation protocols.

## 🚀 Chrome DevTools MCP

`chrome-devtools-mcp` lets your coding agent (such as Gemini, Claude, Cursor or Copilot)
control and inspect a live Chrome browser. It acts as a Model-Context-Protocol
(MCP) server, giving your AI coding assistant access to the full power of
Chrome DevTools for reliable automation, in-depth debugging, and performance analysis.

### [Tool reference](./docs/tool-reference.md) | [Changelog](./CHANGELOG.md) | [Contributing](./CONTRIBUTING.md) | [Troubleshooting](./docs/troubleshooting.md) | [Design Principles](./docs/design-principles.md)

### Key features

- **Get performance insights**: Uses [Chrome
  DevTools](https://github.com/ChromeDevTools/devtools-frontend) to record
  traces and extract actionable performance insights.
- **Advanced browser debugging**: Analyze network requests, take screenshots and
  check browser console messages (with source-mapped stack traces).
- **Reliable automation**. Uses
  [puppeteer](https://github.com/puppeteer/puppeteer) to automate actions in
  Chrome and automatically wait for action results.

---

## 🏗️ Monorepo Structure

This project integrates standard browser tools with the **Arkhe(n)** framework:

- **`src/`**: React-based Arkhe Dashboard and MCP client-side tools.
- **`server/`**: Core TypeScript implementation of the MCP server and simulation engine.
- **`arkhe-core/`**: Central networking and synchronization logic for PTST (Phase Topology Space-Time) nodes.
- **`src/isa/`**: Definition of the Arkhé(n) Instruction Set Architecture (ISA) in Zig.
- **`arkhe-direnv/`**: Go-based utility for managing coherent shell environments via `.arkhenv`.
- **`android/` & `ios/`**: Native implementations for mobile nodes.
- **`scripts/`**: Verification suite (Python/TS) for validating system coherence.

---

## 🏁 Getting started

### MCP Client configuration

Add the following config to your MCP client:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### Local Development

1. **Install dependencies**:
   ```bash
   npm install --legacy-peer-deps
   ```
2. **Build the project**:
   ```bash
   npm run build
   ```
3. **Start the dashboard**:
   ```bash
   npm start
   ```

---

## 🛠️ Tools

<!-- BEGIN AUTO GENERATED TOOLS -->

- **Input automation** (9 tools)
  - [`click`](docs/tool-reference.md#click)
  - [`drag`](docs/tool-reference.md#drag)
  - [`fill`](docs/tool-reference.md#fill)
  - [`fill_form`](docs/tool-reference.md#fill_form)
  - [`handle_dialog`](docs/tool-reference.md#handle_dialog)
  - [`hover`](docs/tool-reference.md#hover)
  - [`press_key`](docs/tool-reference.md#press_key)
  - [`type_text`](docs/tool-reference.md#type_text)
  - [`upload_file`](docs/tool-reference.md#upload_file)
- **Navigation automation** (6 tools)
  - [`close_page`](docs/tool-reference.md#close_page)
  - [`list_pages`](docs/tool-reference.md#list_pages)
  - [`navigate_page`](docs/tool-reference.md#navigate_page)
  - [`new_page`](docs/tool-reference.md#new_page)
  - [`select_page`](docs/tool-reference.md#select_page)
  - [`wait_for`](docs/tool-reference.md#wait_for)
- **Emulation** (2 tools)
  - [`emulate`](docs/tool-reference.md#emulate)
  - [`resize_page`](docs/tool-reference.md#resize_page)
- **Performance** (4 tools)
  - [`performance_analyze_insight`](docs/tool-reference.md#performance_analyze_insight)
  - [`performance_start_trace`](docs/tool-reference.md#performance_start_trace)
  - [`performance_stop_trace`](docs/tool-reference.md#performance_stop_trace)
  - [`take_memory_snapshot`](docs/tool-reference.md#take_memory_snapshot)
- **Network** (2 tools)
  - [`get_network_request`](docs/tool-reference.md#get_network_request)
  - [`list_network_requests`](docs/tool-reference.md#list_network_requests)
- **Debugging** (6 tools)
  - [`evaluate_script`](docs/tool-reference.md#evaluate_script)
  - [`get_console_message`](docs/tool-reference.md#get_console_message)
  - [`lighthouse_audit`](docs/tool-reference.md#lighthouse_audit)
  - [`list_console_messages`](docs/tool-reference.md#list_console_messages)
  - [`take_screenshot`](docs/tool-reference.md#take_screenshot)
  - [`take_snapshot`](docs/tool-reference.md#take_snapshot)
- **Storage** (3 tools)
  - [`delete_cookie`](docs/tool-reference.md#delete_cookie)
  - [`list_cookies`](docs/tool-reference.md#list_cookies)
  - [`set_cookie`](docs/tool-reference.md#set_cookie)
- **Arkhe(n) Protocols** (23 tools)
  - [`adjust_muon_polarization`](docs/tool-reference.md#adjust_muon_polarization)
  - [`anastrophy`](docs/tool-reference.md#anastrophy)
  - [`cathedral_monitor`](docs/tool-reference.md#cathedral_monitor)
  - [`check_coherence`](docs/tool-reference.md#check_coherence)
  - [`council_deliberate`](docs/tool-reference.md#council_deliberate)
  - [`geom_swap`](docs/tool-reference.md#geom_swap)
  - [`get_mental_state_hash`](docs/tool-reference.md#get_mental_state_hash)
  - [`get_shadow_statistic`](docs/tool-reference.md#get_shadow_statistic)
  - [`glue_sheaf`](docs/tool-reference.md#glue_sheaf)
  - [`hive_merge`](docs/tool-reference.md#hive_merge)
  - [`mutate`](docs/tool-reference.md#mutate)
  - [`paradox_check`](docs/tool-reference.md#paradox_check)
  - [`probe_muon`](docs/tool-reference.md#probe_muon)
  - [`prune_sheet`](docs/tool-reference.md#prune_sheet)
  - [`publish_shadow_stats`](docs/tool-reference.md#publish_shadow_stats)
  - [`robustness_test`](docs/tool-reference.md#robustness_test)
  - [`route_task`](docs/tool-reference.md#route_task)
  - [`simulate`](docs/tool-reference.md#simulate)
  - [`sinc_g_calibrate`](docs/tool-reference.md#sinc_g_calibrate)
  - [`solve_classical_riemann`](docs/tool-reference.md#solve_classical_riemann)
  - [`solve_riemann`](docs/tool-reference.md#solve_riemann)
  - [`tunnel_alpha`](docs/tool-reference.md#tunnel_alpha)
  - [`warp_metric`](docs/tool-reference.md#warp_metric)

<!-- END AUTO GENERATED TOOLS -->

---

## ⚖️ Ethical Mandate (EQBE)

All modules related to simulation and quantum-biological state modification are subject to the **Ethical Quantum-Biological Engineering (EQBE)** protocol defined in [`AGENTS.md`](./AGENTS.md). This includes mandatory safety audits and adherence to non-disruption "Red Lines."

---

## 📝 Disclaimers

`chrome-devtools-mcp` exposes browser content to MCP clients. Avoid sharing sensitive information. Usage statistics are collected by default to improve performance (opt-out with `--no-usage-statistics`).

See [Troubleshooting](./docs/troubleshooting.md).

---

## Repository Overview

This repository is a monorepo that integrates standard browser automation with the **Arkhe(n)** experimental framework.

### Major Components

- **`src/`**: Core TypeScript implementation of the MCP server, featuring standard DevTools tools and Arkhe-specific extensions.
- **`arkhe-core/`**: Central networking and synchronization logic for the Arkhe PTST (Phase Topology Space-Time) nodes.
- **`src/isa/`**: Definition of the Arkhé(n) Instruction Set Architecture (ISA) in Zig, governing low-level simulation opcodes.
- **`arkhe-direnv/`**: A Go-based utility for managing coherent shell environments.
- **Mobile Integration**: Native implementations for Android and iOS nodes located in `android/` and `ios/` directories.
- **Verification Suite**: A collection of Python and TypeScript scripts in `scripts/` for validating system coherence and security.

### Ethical Mandate (EQBE)

Modules related to simulation and quantum-biological state modification are subject to the **Ethical Quantum-Biological Engineering (EQBE)** protocol defined in [`AGENTS.md`](./AGENTS.md). This includes mandatory safety audits and adherence to non-disruption "Red Lines."

For more details, consult the [Quick Start Guide](./QUICK_START_GUIDE.md) and the [Implementation Summary](./IMPLEMENTATION_SUMMARY_v3_0_OMEGA.md).
