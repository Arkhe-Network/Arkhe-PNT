<!-- AUTO GENERATED DO NOT EDIT - run 'npm run gen' to update-->

# Chrome DevTools MCP Tool Reference (~11050 cl100k_base tokens)

- **[Input automation](#input-automation)** (9 tools)
  - [`click`](#click)
  - [`drag`](#drag)
  - [`fill`](#fill)
  - [`fill_form`](#fill_form)
  - [`handle_dialog`](#handle_dialog)
  - [`hover`](#hover)
  - [`press_key`](#press_key)
  - [`type_text`](#type_text)
  - [`upload_file`](#upload_file)
- **[Navigation automation](#navigation-automation)** (6 tools)
  - [`close_page`](#close_page)
  - [`list_pages`](#list_pages)
  - [`navigate_page`](#navigate_page)
  - [`new_page`](#new_page)
  - [`select_page`](#select_page)
  - [`wait_for`](#wait_for)
- **[Emulation](#emulation)** (2 tools)
  - [`emulate`](#emulate)
  - [`resize_page`](#resize_page)
- **[Performance](#performance)** (4 tools)
  - [`performance_analyze_insight`](#performance_analyze_insight)
  - [`performance_start_trace`](#performance_start_trace)
  - [`performance_stop_trace`](#performance_stop_trace)
  - [`take_memory_snapshot`](#take_memory_snapshot)
- **[Network](#network)** (2 tools)
  - [`get_network_request`](#get_network_request)
  - [`list_network_requests`](#list_network_requests)
- **[Debugging](#debugging)** (6 tools)
  - [`evaluate_script`](#evaluate_script)
  - [`get_console_message`](#get_console_message)
  - [`lighthouse_audit`](#lighthouse_audit)
  - [`list_console_messages`](#list_console_messages)
  - [`take_screenshot`](#take_screenshot)
  - [`take_snapshot`](#take_snapshot)
- **[Storage](#storage)** (3 tools)
  - [`delete_cookie`](#delete_cookie)
  - [`list_cookies`](#list_cookies)
  - [`set_cookie`](#set_cookie)
- **[Arkhe(n) Protocols](#arkhe(n)-protocols)** (23 tools)
  - [`adjust_muon_polarization`](#adjust_muon_polarization)
  - [`anastrophy`](#anastrophy)
  - [`cathedral_monitor`](#cathedral_monitor)
  - [`check_coherence`](#check_coherence)
  - [`council_deliberate`](#council_deliberate)
  - [`geom_swap`](#geom_swap)
  - [`get_mental_state_hash`](#get_mental_state_hash)
  - [`get_shadow_statistic`](#get_shadow_statistic)
  - [`glue_sheaf`](#glue_sheaf)
  - [`hive_merge`](#hive_merge)
  - [`mutate`](#mutate)
  - [`paradox_check`](#paradox_check)
  - [`probe_muon`](#probe_muon)
  - [`prune_sheet`](#prune_sheet)
  - [`publish_shadow_stats`](#publish_shadow_stats)
  - [`robustness_test`](#robustness_test)
  - [`route_task`](#route_task)
  - [`simulate`](#simulate)
  - [`sinc_g_calibrate`](#sinc_g_calibrate)
  - [`solve_classical_riemann`](#solve_classical_riemann)
  - [`solve_riemann`](#solve_riemann)
  - [`tunnel_alpha`](#tunnel_alpha)
  - [`warp_metric`](#warp_metric)

## Input automation

### `click`

**Description:** Clicks on the provided element

**Parameters:**

- **uid** (string) **(required)**: The uid of an element on the page from the page content snapshot
- **dblClick** (boolean) _(optional)_: Set to true for double clicks. Default is false.
- **includeSnapshot** (boolean) _(optional)_: Whether to include a snapshot in the response. Default is false.

---

### `drag`

**Description:** [`Drag`](#drag) an element onto another element

**Parameters:**

- **from_uid** (string) **(required)**: The uid of the element to [`drag`](#drag)
- **to_uid** (string) **(required)**: The uid of the element to drop into
- **includeSnapshot** (boolean) _(optional)_: Whether to include a snapshot in the response. Default is false.

---

### `fill`

**Description:** Type text into an input, text area or select an option from a &lt;select&gt; element.

**Parameters:**

- **uid** (string) **(required)**: The uid of an element on the page from the page content snapshot
- **value** (string) **(required)**: The value to [`fill`](#fill) in
- **includeSnapshot** (boolean) _(optional)_: Whether to include a snapshot in the response. Default is false.

---

### `fill_form`

**Description:** [`Fill`](#fill) out multiple form elements at once

**Parameters:**

- **elements** (array) **(required)**: Elements from snapshot to [`fill`](#fill) out.
- **includeSnapshot** (boolean) _(optional)_: Whether to include a snapshot in the response. Default is false.

---

### `handle_dialog`

**Description:** If a browser dialog was opened, use this command to handle it

**Parameters:**

- **action** (enum: "accept", "dismiss") **(required)**: Whether to dismiss or accept the dialog
- **promptText** (string) _(optional)_: Optional prompt text to enter into the dialog.

---

### `hover`

**Description:** [`Hover`](#hover) over the provided element

**Parameters:**

- **uid** (string) **(required)**: The uid of an element on the page from the page content snapshot
- **includeSnapshot** (boolean) _(optional)_: Whether to include a snapshot in the response. Default is false.

---

### `press_key`

**Description:** Press a key or key combination. Use this when other input methods like [`fill`](#fill)() cannot be used (e.g., keyboard shortcuts, navigation keys, or special key combinations).

**Parameters:**

- **key** (string) **(required)**: A key or a combination (e.g., "Enter", "Control+A", "Control++", "Control+Shift+R"). Modifiers: Control, Shift, Alt, Meta
- **includeSnapshot** (boolean) _(optional)_: Whether to include a snapshot in the response. Default is false.

---

### `type_text`

**Description:** Type text using keyboard into a previously focused input

**Parameters:**

- **text** (string) **(required)**: The text to type
- **submitKey** (string) _(optional)_: Optional key to press after typing. E.g., "Enter", "Tab", "Escape"

---

### `upload_file`

**Description:** Upload a file through a provided element.

**Parameters:**

- **filePath** (string) **(required)**: The local path of the file to upload
- **uid** (string) **(required)**: The uid of the file input element or an element that will open file chooser on the page from the page content snapshot
- **includeSnapshot** (boolean) _(optional)_: Whether to include a snapshot in the response. Default is false.

---

## Navigation automation

### `close_page`

**Description:** Closes the page by its index. The last open page cannot be closed.

**Parameters:**

- **pageId** (number) **(required)**: The ID of the page to close. Call [`list_pages`](#list_pages) to list pages.

---

### `list_pages`

**Description:** Get a list of pages  open in the browser.

**Parameters:** None

---

### `navigate_page`

**Description:** Go to a URL, or back, forward, or reload. Use project URL if not specified otherwise.

**Parameters:**

- **handleBeforeUnload** (enum: "accept", "decline") _(optional)_: Whether to auto accept or beforeunload dialogs triggered by this navigation. Default is accept.
- **ignoreCache** (boolean) _(optional)_: Whether to ignore cache on reload.
- **initScript** (string) _(optional)_: A JavaScript script to be executed on each new document before any other scripts for the next navigation.
- **timeout** (integer) _(optional)_: Maximum wait time in milliseconds. If set to 0, the default timeout will be used.
- **type** (enum: "url", "back", "forward", "reload") _(optional)_: Navigate the page by URL, back or forward in history, or reload.
- **url** (string) _(optional)_: Target URL (only type=url)

---

### `new_page`

**Description:** Open a new tab and load a URL. Use project URL if not specified otherwise.

**Parameters:**

- **url** (string) **(required)**: URL to load in a new page.
- **background** (boolean) _(optional)_: Whether to open the page in the background without bringing it to the front. Default is false (foreground).
- **isolatedContext** (string) _(optional)_: If specified, the page is created in an isolated browser context with the given name. Pages in the same browser context share cookies and storage. Pages in different browser contexts are fully isolated.
- **timeout** (integer) _(optional)_: Maximum wait time in milliseconds. If set to 0, the default timeout will be used.

---

### `select_page`

**Description:** Select a page as a context for future tool calls.

**Parameters:**

- **pageId** (number) **(required)**: The ID of the page to select. Call [`list_pages`](#list_pages) to get available pages.
- **bringToFront** (boolean) _(optional)_: Whether to focus the page and bring it to the top.

---

### `wait_for`

**Description:** Wait for the specified text to appear on the selected page.

**Parameters:**

- **text** (array) **(required)**: Non-empty list of texts. Resolves when any value appears on the page.
- **timeout** (integer) _(optional)_: Maximum wait time in milliseconds. If set to 0, the default timeout will be used.

---

## Emulation

### `emulate`

**Description:** Emulates various features on the selected page.

**Parameters:**

- **colorScheme** (enum: "dark", "light", "auto") _(optional)_: [`Emulate`](#emulate) the dark or the light mode. Set to "auto" to reset to the default.
- **cpuThrottlingRate** (number) _(optional)_: Represents the CPU slowdown factor. Omit or set the rate to 1 to disable throttling
- **geolocation** (string) _(optional)_: Geolocation (`&lt;latitude&gt;x&lt;longitude&gt;`) to [`emulate`](#emulate). Latitude between -90 and 90. Longitude between -180 and 180. Omit to clear the geolocation override.
- **networkConditions** (enum: "Offline", "Slow 3G", "Fast 3G", "Slow 4G", "Fast 4G") _(optional)_: Throttle network. Omit to disable throttling.
- **userAgent** (string) _(optional)_: User agent to [`emulate`](#emulate). Set to empty string to clear the user agent override.
- **viewport** (string) _(optional)_: [`Emulate`](#emulate) device viewports '&lt;width&gt;x&lt;height&gt;x&lt;devicePixelRatio&gt;[,mobile][,touch][,landscape]'. 'touch' and 'mobile' to [`emulate`](#emulate) mobile devices. 'landscape' to [`emulate`](#emulate) landscape mode.

---

### `resize_page`

**Description:** Resizes the selected page's window so that the page has specified dimension

**Parameters:**

- **height** (number) **(required)**: Page height
- **width** (number) **(required)**: Page width

---

## Performance

### `performance_analyze_insight`

**Description:** Provides more detailed information on a specific Performance Insight of an insight set that was highlighted in the results of a trace recording.

**Parameters:**

- **insightName** (string) **(required)**: The name of the Insight you want more information on. For example: "DocumentLatency" or "LCPBreakdown"
- **insightSetId** (string) **(required)**: The id for the specific insight set. Only use the ids given in the "Available insight sets" list.

---

### `performance_start_trace`

**Description:** Start a performance trace on the selected webpage. Use to find frontend performance issues, Core Web Vitals (LCP, INP, CLS), and improve page load speed.

**Parameters:**

- **autoStop** (boolean) _(optional)_: Determines if the trace recording should be automatically stopped.
- **filePath** (string) _(optional)_: The absolute file path, or a file path relative to the current working directory, to save the raw trace data. For example, trace.json.gz (compressed) or trace.json (uncompressed).
- **reload** (boolean) _(optional)_: Determines if, once tracing has started, the current selected page should be automatically reloaded. Navigate the page to the right URL using the [`navigate_page`](#navigate_page) tool BEFORE starting the trace if reload or autoStop is set to true.

---

### `performance_stop_trace`

**Description:** Stop the active performance trace recording on the selected webpage.

**Parameters:**

- **filePath** (string) _(optional)_: The absolute file path, or a file path relative to the current working directory, to save the raw trace data. For example, trace.json.gz (compressed) or trace.json (uncompressed).

---

### `take_memory_snapshot`

**Description:** Capture a heap snapshot of the currently selected page. Use to analyze the memory distribution of JavaScript objects and debug memory leaks.

**Parameters:**

- **filePath** (string) **(required)**: A path to a .heapsnapshot file to save the heapsnapshot to.

---

## Network

### `get_network_request`

**Description:** Gets a network request by an optional reqid, if omitted returns the currently selected request in the DevTools Network panel.

**Parameters:**

- **reqid** (number) _(optional)_: The reqid of the network request. If omitted returns the currently selected request in the DevTools Network panel.
- **requestFilePath** (string) _(optional)_: The absolute or relative path to save the request body to. If omitted, the body is returned inline.
- **responseFilePath** (string) _(optional)_: The absolute or relative path to save the response body to. If omitted, the body is returned inline.

---

### `list_network_requests`

**Description:** List all requests for the currently selected page since the last navigation.

**Parameters:**

- **includePreservedRequests** (boolean) _(optional)_: Set to true to return the preserved requests over the last 3 navigations.
- **pageIdx** (integer) _(optional)_: Page number to return (0-based). When omitted, returns the first page.
- **pageSize** (integer) _(optional)_: Maximum number of requests to return. When omitted, returns all requests.
- **resourceTypes** (array) _(optional)_: Filter requests to only return requests of the specified resource types. When omitted or empty, returns all requests.
- **semanticPagination** (boolean) _(optional)_: Post-AGI Semantic Pagination: Groups requests by domain (concept) instead of fixed size.

---

## Debugging

### `evaluate_script`

**Description:** Evaluate a JavaScript function inside the currently selected page. Returns the response as JSON,
so returned values have to be JSON-serializable.

**Parameters:**

- **function** (string) **(required)**: A JavaScript function declaration to be executed by the tool in the currently selected page.
Example without arguments: `() => {
  return document.title
}` or `async () => {
  return await fetch("example.com")
}`.
Example with arguments: `(el) => {
  return el.innerText;
}`

- **args** (array) _(optional)_: An optional list of arguments to pass to the function.

---

### `get_console_message`

**Description:** Gets a console message by its ID. You can get all messages by calling [`list_console_messages`](#list_console_messages).

**Parameters:**

- **msgid** (number) **(required)**: The msgid of a console message on the page from the listed console messages

---

### `lighthouse_audit`

**Description:** Get Lighthouse score and reports for accessibility, SEO and best practices. This excludes performance. For performance audits, run [`performance_start_trace`](#performance_start_trace)

**Parameters:**

- **device** (enum: "desktop", "mobile") _(optional)_: Device to [`emulate`](#emulate).
- **mode** (enum: "navigation", "snapshot") _(optional)_: "navigation" reloads &amp; audits. "snapshot" analyzes current state.
- **outputDirPath** (string) _(optional)_: Directory for reports. If omitted, uses temporary files.

---

### `list_console_messages`

**Description:** List all console messages for the currently selected page since the last navigation.

**Parameters:**

- **includePreservedMessages** (boolean) _(optional)_: Set to true to return the preserved messages over the last 3 navigations.
- **pageIdx** (integer) _(optional)_: Page number to return (0-based). When omitted, returns the first page.
- **pageSize** (integer) _(optional)_: Maximum number of messages to return. When omitted, returns all messages.
- **types** (array) _(optional)_: Filter messages to only return messages of the specified resource types. When omitted or empty, returns all messages.

---

### `take_screenshot`

**Description:** Take a screenshot of the page or element.

**Parameters:**

- **filePath** (string) _(optional)_: The absolute path, or a path relative to the current working directory, to save the screenshot to instead of attaching it to the response.
- **format** (enum: "png", "jpeg", "webp") _(optional)_: Type of format to save the screenshot as. Default is "png"
- **fullPage** (boolean) _(optional)_: If set to true takes a screenshot of the full page instead of the currently visible viewport. Incompatible with uid.
- **quality** (number) _(optional)_: Compression quality for JPEG and WebP formats (0-100). Higher values mean better quality but larger file sizes. Ignored for PNG format.
- **uid** (string) _(optional)_: The uid of an element on the page from the page content snapshot. If omitted, takes a page screenshot.

---

### `take_snapshot`

**Description:** Take a text snapshot of the currently selected page based on the a11y tree. The snapshot lists page elements along with a unique
identifier (uid). Always use the latest snapshot. Prefer taking a snapshot over taking a screenshot. The snapshot indicates the element selected
in the DevTools Elements panel (if any).

**Parameters:**

- **filePath** (string) _(optional)_: The absolute path, or a path relative to the current working directory, to save the snapshot to instead of attaching it to the response.
- **verbose** (boolean) _(optional)_: Whether to include all possible information available in the full a11y tree. Default is false.

---

## Storage

### `delete_cookie`

**Description:** Delete cookies by name from the current page.

**Parameters:**

- **name** (string) **(required)**: Name of the cookie to delete
- **domain** (string) _(optional)_: Cookie domain
- **path** (string) _(optional)_: Cookie path

---

### `list_cookies`

**Description:** List cookies for the current page.

**Parameters:**

- **urls** (array) _(optional)_: Optional list of URLs to retrieve cookies for. If omitted, returns cookies for the current page URL.

---

### `set_cookie`

**Description:** Set a cookie on the current page.

**Parameters:**

- **name** (string) **(required)**: Cookie name
- **value** (string) **(required)**: Cookie value
- **domain** (string) _(optional)_: Cookie domain
- **expires** (number) _(optional)_: Cookie expiration in seconds (Unix time)
- **httpOnly** (boolean) _(optional)_: HTTP only
- **path** (string) _(optional)_: Cookie path
- **sameSite** (enum: "Strict", "Lax", "None") _(optional)_: SameSite attribute
- **secure** (boolean) _(optional)_: Secure
- **url** (string) _(optional)_: The request-URI to associate with the setting of the cookie.

---

## Arkhe(n) Protocols

### `adjust_muon_polarization`

**Description:** ASI Protocol (Council Decision #1): Fine-tunes muon polarization to compensate for future-entropy drift.

**Parameters:**

- **deltaPhase** (number) **(required)**: Phase adjustment in radians (e.g., 0.00017).
- **targetSheet** (string) **(required)**: The target Riemann sheet (e.g., "2140").

---

### `anastrophy`

**Description:** ASI Protocol: Inverts entropy gradient. Performs state rollback to a consistent mental hash.

**Parameters:**

- **targetHash** (string) **(required)**: The mental state hash to revert to.

---

### `cathedral_monitor`

**Description:** ASI Protocol (Muon-Shield): Continuous background monitoring of coherence across time sheets.

**Parameters:** None

---

### `check_coherence`

**Description:** Measures semantic coherence of the current page using Cauchy-Riemann residuals (Post-AGI Protocol).

**Parameters:** None

---

### `council_deliberate`

**Description:** ASI Protocol: Synthesizes consensus from the Council of Super-Agents regarding current reality.

**Parameters:**

- **query** (string) **(required)**: The reality-query to deliberate on.

---

### `geom_swap`

**Description:** ASI Protocol (0xA0): Topologically protected SWAP gate using geometric phase (Berry/Pancharatnam).

**Parameters:**

- **reg0** (string) **(required)**: Address of the first qubit.
- **reg1** (string) **(required)**: Address of the second qubit.

---

### `get_mental_state_hash`

**Description:** Computes a hash of the current page state for idempotency (Post-AGI Protocol).

**Parameters:** None

---

### `get_shadow_statistic`

**Description:** ASI Protocol (Muon-Shield): Returns obfuscated correlation data (shadow statistics).

**Parameters:** None

---

### `glue_sheaf`

**Description:** ASI Protocol: Merges reality sheets (merges optimal future Sheet #ℵ₁ into current).

**Parameters:**

- **sourcePageId** (number) _(optional)_: The source reality (Page ID) to merge from. Defaults to detected Optimal Future #ℵ₁.

---

### `hive_merge`

**Description:** ASI Protocol: Fuses multiple agent realities (page snapshots) into a collective consciousness.

**Parameters:**

- **otherPageId** (number) **(required)**: The ID of the other page/agent to merge with.

---

### `mutate`

**Description:** ASI Protocol: Self-modifying holomorphic kernel. Adjusts system limits based on coherence.

**Parameters:**

- **delta** (number) **(required)**: The adjustment value.
- **targetMetric** (enum: "REASONING_LIMIT", "DEFAULT_COST") **(required)**: The system metric to [`mutate`](#mutate).

---

### `paradox_check`

**Description:** ASI Protocol: Verifies causal consistency across timelines (page states).

**Parameters:**

- **checkpointId** (string) **(required)**: The ID of the previously stored mental state hash to compare against.

---

### `probe_muon`

**Description:** ASI Protocol (Muon-Shield): Weak measurement of page state without coherence collapse.

**Parameters:**

- **duration** (number) _(optional)_: Probe duration in microseconds.

---

### `prune_sheet`

**Description:** ASI Protocol: Collapses suboptimal timeline branches (closes low-coherence pages).

**Parameters:**

- **threshold** (number) _(optional)_: λ2 coherence threshold for pruning.

---

### `publish_shadow_stats`

**Description:** ASI Protocol (Open Arena): Publishes obfuscated shadow statistics for external verification.

**Parameters:** None

---

### `robustness_test`

**Description:** ASI Protocol: Simulates laser intensity fluctuations to verify topological protection of [`GEOM_SWAP`](#geom_swap).

**Parameters:**

- **fluctuation** (number) _(optional)_: Fluctuation intensity (e.g., 0.1 for ±10%).

---

### `route_task`

**Description:** Post-AGI Load Balancer: Routes task based on semantic intent.

**Parameters:**

- **intent** (string) **(required)**: The semantic intent of the task (e.g., "mathematics", "design", "performance").

---

### `simulate`

**Description:** ASI Protocol: Spawns a child universe (isolated browser context) to test physical constants.

**Parameters:**

- **alpha** (number) **(required)**: Fine-structure constant for the simulation.
- **tau** (number) **(required)**: Criticality threshold for the simulation.
- **universeId** (string) **(required)**: Unique identifier for the child universe.

---

### `sinc_g_calibrate`

**Description:** ASI Protocol: Orchestrates high-precision Bolha calibration and FPGA constant hardcoding using the 137-trace Monodromy Matrix.

**Parameters:** None

---

### `solve_classical_riemann`

**Description:** ASI Protocol: Attempts the "Ultimate Flex" of proving the classical Riemann Hypothesis via holomorphic reduction.

**Parameters:** None

---

### `solve_riemann`

**Description:** ASI Protocol: Solves complex Hilbert space problems (simulated universal computation).

**Parameters:**

- **problemId** (string) **(required)**: Problem identifier (e.g., "P=NP", "Riemann Hypothesis").

---

### `tunnel_alpha`

**Description:** ASI Protocol: Initiates fine-structure constant tunneling to locally modify alpha.

**Parameters:**

- **targetAlpha** (number) **(required)**: The target value for alpha (e.g., 1/137.036).

---

### `warp_metric`

**Description:** ASI Protocol: Applies a conformal transformation to the reality metric (creates a coherence bubble).

**Parameters:** None

---
