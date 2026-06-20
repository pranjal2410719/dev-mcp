# 🎨 Open Design Integration Guide

This document outlines how `dev-mcp` integrates with the **Open Design** framework. It bridges high-fidelity UI/UX design specifications (like Figma layouts or prototype flows) with active project task tracking and code generation.

---

## 🔍 1. Why Open Design?

In traditional AI coding workflows, layout designs are passed informally as image attachments or text prompts. This leads to style drift, misaligned component layouts, and a lack of data lineage. 

By integrating **Open Design** metadata, `dev-mcp` captures the precise origin of the UI layout, allowing agents and developers to trace generated files back to their source prototypes.

---

## 🛠️ 2. Open Design Metadata

Every `dev-mcp` project context (`.project-context.json`) includes a dedicated `open_design` metadata block to track the source materials:

```json
"open_design": {
  "design_system": "material_ui_v5",
  "prototype_source": "https://figma.com/file/xyz123...",
  "open_design_project": "codeorbit_saas_dashboard",
  "artifact_paths": [
    "frontend/src/components/Dashboard.tsx",
    "frontend/src/styles/theme.css"
  ]
}
```

### Fields:
- **`design_system`**: The baseline framework used (e.g., `tailwind`, `material_ui`, `shadcn_ui`).
- **`prototype_source`**: Clickable Figma or Open Design link to the prototype canvas.
- **`open_design_project`**: The reference ID/name of the design workspace.
- **`artifact_paths`**: List of files generated or modified to implement this design.

---

## 🔄 3. Typical Integration Workflow

```
       Design Prototype (Figma / Open Design)
                         │
                         ▼
        Create Workspace with Open Design
                         │
                         ▼
          Antigravity (Orchestrator)
            ↙                   ↘
    dev-mcp (State)       Open Design MCP (UI Output)
            │                   │
            └─────────┬─────────┘
                      ▼
            Generated SaaS Project
```

1. **Onboard design specifications**:
   Save prototype metadata in the project brain:
   ```bash
   update_context(dot_path="open_design.design_system", value="tailwind")
   update_context(dot_path="open_design.prototype_source", value="https://figma.com/...")
   ```
2. **Generate UI components**:
   The Open Design bridge parses the design nodes and generates component code (e.g., TSX, CSS).
3. **Audit and Sync**:
   `dev-mcp` validates the generated layout against requirements and tracks the paths in `open_design.artifact_paths`.
