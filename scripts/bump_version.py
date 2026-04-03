import sys
import os
import json

def bump_version(part='patch'):
    if not os.path.exists('VERSION'):
        with open('VERSION', 'w') as f:
            f.write('1.0.0')

    with open('VERSION', 'r') as f:
        version = f.read().strip()

    major, minor, patch = map(int, version.split('.'))

    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    with open('VERSION', 'w') as f:
        f.write(new_version)

    print(f"🜏 Version bumped to {new_version}")

    # Update package.json
    if os.path.exists('package.json'):
        with open('package.json', 'r') as f:
            data = json.load(f)
        data['version'] = new_version
        with open('package.json', 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
        print(f"🜏 package.json updated to {new_version}")

if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    bump_version(part)
