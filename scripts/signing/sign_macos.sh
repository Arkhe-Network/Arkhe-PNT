#!/bin/bash
set -e

# Arkhe(n) macOS Code Signing & Notarization
# Usage: ./sign_macos.sh <path_to_app_or_dmg> <apple_id> <team_id> <app_specific_password> <signing_identity>

TARGET=$1
APPLE_ID=$2
TEAM_ID=$3
PASSWORD=$4
IDENTITY=$5

if [ -z "$TARGET" ] || [ -z "$APPLE_ID" ] || [ -z "$TEAM_ID" ] || [ -z "$PASSWORD" ] || [ -z "$IDENTITY" ]; then
    echo "Usage: $0 <target> <apple_id> <team_id> <password> <identity>"
    echo "Example: $0 build/Arkhe.app admin@arkhe.network AB12345678 abcd-efgh-ijkl-mnop 'Developer ID Application: Arkhe Network (AB12345678)'"
    exit 1
fi

echo "🜏 [1/4] Signing Mach-O binaries (.dylib, .so) and the main target with identity: $IDENTITY..."
# Find and sign all nested dynamic libraries and shared objects first
if [ -d "$TARGET" ]; then
    find "$TARGET" -type f \( -name "*.dylib" -o -name "*.so" \) -exec codesign --force --verify --verbose --timestamp --options runtime --sign "$IDENTITY" {} \;
fi

# --deep: sign nested code and frameworks
# --options runtime: enable hardened runtime (mandatory for Apple notarization)
# --timestamp: include secure timestamp from Apple
codesign --deep --force --verify --verbose --timestamp --options runtime --sign "$IDENTITY" "$TARGET"

echo "🜏 [2/4] Packaging for Notarization..."
ZIP_PATH="${TARGET}.zip"
/usr/bin/ditto -c -k --keepParent "$TARGET" "$ZIP_PATH"

echo "🜏 [3/4] Submitting to Apple Notary Service..."
# Submit to Apple and wait for the result
xcrun notarytool submit "$ZIP_PATH" --apple-id "$APPLE_ID" --team-id "$TEAM_ID" --password "$PASSWORD" --wait

echo "🜏 [4/4] Stapling Notarization Ticket..."
# Staple the ticket to the app/dmg so it can be verified offline by Gatekeeper
xcrun stapler staple "$TARGET"

# Cleanup
rm "$ZIP_PATH"

echo "🜏 macOS Signing & Notarization Complete: $TARGET"
# Verify the final signature
spctl -a -t exec -vv "$TARGET"
