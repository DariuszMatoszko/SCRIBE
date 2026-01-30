#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP_DIR="$HOME/Applications"
APP_NAME="SCRIBE Panel.app"
mkdir -p "$APP_DIR"

# tworz .app (AppleScript droplet)
cat > "$APP_DIR/$APP_NAME/Contents/Info.plist" <<EOF2
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>SCRIBE Panel</string>
  <key>CFBundleIdentifier</key><string>com.dariusz.scribe.panel</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleExecutable</key><string>applet</string>
  <key>LSUIElement</key><false/>
</dict>
</plist>
EOF2

mkdir -p "$APP_DIR/$APP_NAME/Contents/MacOS"
cat > "$APP_DIR/$APP_NAME/Contents/MacOS/applet" <<EOF2
#!/bin/bash
cd "$ROOT"
mkdir -p logs
/usr/bin/python3 -m scribe_web --panel >> logs/launch_panel.log 2>&1
EOF2

chmod +x "$APP_DIR/$APP_NAME/Contents/MacOS/applet"

echo "OK: Zainstalowano $APP_DIR/$APP_NAME"
echo "Uruchom z Launchpad (wyszukaj: SCRIBE Panel) lub przypnij do Docka."
echo "Log: $ROOT/logs/launch_panel.log"
echo ""
echo "Nacisnij ENTER aby zamknac..."
read
