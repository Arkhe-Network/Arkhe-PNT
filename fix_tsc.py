import os

def fix_file(filepath, search, replace):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        new_content = content.replace(search, replace)
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")

# The error is likely because the environment doesn't have the right dependencies or config
# but we can try to fix the obvious TS errors in skills/arkhe_skills.ts

# Debugger breakthrough check
# In vs_omega.zig: Breakthrough is void Reality breakthrough(marker: []const u8) void
# But the error says: Property 'info' does not exist on type 'Debugger'.
# We need to see where Debugger is defined in TS context.
