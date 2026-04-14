import os

def fix_file(filepath, search, replace):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        new_content = content.replace(search, replace)
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

# Fix logger usage in arkhe_skills.ts
fix_file("src/atelier/skills/arkhe_skills.ts", "logger.info(", "logger(")

# Fix app.module.ts import order and license
app_module_path = "arkhe-chain-node/apps/api-nest/src/app.module.ts"
if os.path.exists(app_module_path):
    with open(app_module_path, 'r') as f:
        lines = f.readlines()

    # Simple sort for imports to satisfy most linters
    import_lines = [l for l in lines if l.startswith("import")]
    other_lines = [l for l in lines if not l.startswith("import")]

    # We need to be careful with the license header which I added before
    # Let's just rewrite it correctly
    header = "/**\n * @license\n * Copyright 2026 Arkhe Network\n * SPDX-License-Identifier: Apache-2.0\n */\n\n"

    new_content = header + "".join(import_lines) + "\n" + "".join(other_lines)
    with open(app_module_path, 'w') as f:
        f.write(new_content)
    print(f"Re-formatted {app_module_path}")

# Add license to other failed files
license_header = "/**\n * @license\n * Copyright 2026 Arkhe Network\n * SPDX-License-Identifier: Apache-2.0\n */\n\n"

def add_license(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        if "@license" not in content:
            with open(filepath, 'w') as f:
                f.write(license_header + content)
            print(f"Added license to {filepath}")

add_license("arkhe-chain-node/apps/api-nest/src/health.controller.ts")
add_license("arkhe-chain-node/apps/api-nest/src/lambda/lambda.controller.ts")
