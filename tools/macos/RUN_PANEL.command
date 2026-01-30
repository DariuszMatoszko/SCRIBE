#!/bin/bash
set -e
cd "$(dirname "$0")/../.."
mkdir -p logs
python3 -m scribe_web --panel 2>&1 | tee -a logs/launch_panel.log
echo ""
echo "Nacisnij ENTER aby zamknac..."
read
