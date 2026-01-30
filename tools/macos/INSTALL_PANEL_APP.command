#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP_DIR="$HOME/Applications"
APP_NAME="SCRIBE Panel.app"
APP_PATH="$APP_DIR/$APP_NAME"

mkdir -p "$APP_DIR"
mkdir -p "$APP_PATH/Contents"
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$ROOT/logs"

cat > "$APP_PATH/Contents/Info.plist" <<EOF
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
EOF

cat > "$APP_PATH/Contents/MacOS/applet" <<EOF
#!/bin/bash
cd "$ROOT"
mkdir -p logs
/usr/bin/python3 -m scribe_web --panel >> logs/launch_panel.log 2>&1
EOF

chmod +x "$APP_PATH/Contents/MacOS/applet"

echo "OK: Zainstalowano $APP_PATH"
echo "Uruchom: Launchpad -> wpisz 'SCRIBE Panel' albo otwórz z $APP_DIR"
echo "Log: $ROOT/logs/launch_panel.log"
echo ""
echo "Nacisnij ENTER aby zamknac..."
read
