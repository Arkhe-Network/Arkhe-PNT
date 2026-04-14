import os

def fix_file(filepath, search, replace):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        new_content = content.replace(search, replace)
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

# Fix arkhe_skills.ts
fix_file("src/atelier/skills/arkhe_skills.ts",
         'import { state } from "../../state";',
         'import { state } from "../../../server/state";')

# Fix app.module.ts imports
fix_file("arkhe-chain-node/apps/api-nest/src/app.module.ts",
         "import { join } from 'path';",
         "import { join } from 'node:path';")

# Fix import order in app.module.ts
fix_file("arkhe-chain-node/apps/api-nest/src/app.module.ts",
         "import { LambdaController } from './lambda/lambda.controller';\nimport { HealthController } from './health.controller';",
         "import { HealthController } from './health.controller';\nimport { LambdaController } from './lambda/lambda.controller';")

# Add license headers (simplified)
license_header = "/**\n * @license\n * Copyright 2026 Arkhe Network\n * SPDX-License-Identifier: Apache-2.0\n */\n\n"

def add_license(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        if "@license" not in content:
            with open(filepath, 'w') as f:
                f.write(license_header + content)
            print(f"Added license to {filepath}")

add_license("arkhe-chain-node/apps/api-nest/src/app.module.ts")
add_license("arkhe-chain-node/apps/api-nest/src/health.controller.ts")
add_license("arkhe-chain-node/apps/api-nest/src/lambda/lambda.controller.ts")

if __name__ == "__main__":
    pass
