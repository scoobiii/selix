#!/bin/bash
# Alerta para autoridades sobre Selic > ROI e PLR bloqueado

cd /root/selix/agents/bluesky_bot
source ../../venv/bin/activate

echo "🚨 ALERTA: SELIC > ROI BLOQUEANDO PLR"
echo "======================================"
echo ""
echo "📢 Notificando autoridades:"
echo "   • MPT (@mpt.bsky.social)"
echo "   • TST (@tst.bsky.social)"
echo "   • MTE (@mte.bsky.social)"
echo "   • ANPT (@anpt.bsky.social)"
echo ""

python monitor_selic_roi.py --once

echo ""
echo "✅ Autoridades trabalhistas notificadas!"
echo "🔗 https://bsky.app/profile/selixbr.bsky.social"
