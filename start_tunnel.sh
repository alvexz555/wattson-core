#!/bin/bash

echo "================================="
echo "     WATTSON CORE - TUNNEL"
echo "================================="
echo ""
echo "Iniciando Cloudflare Tunnel..."
echo ""

cloudflared tunnel --url http://localhost:5000 2>&1 | while read -r line; do
    echo "$line"

    if [[ "$line" =~ https://[a-zA-Z0-9-]+\.trycloudflare\.com ]]; then
        TUNNEL_URL="${BASH_REMATCH[0]}"
        echo "$TUNNEL_URL" > backend_url.txt

        echo ""
        echo "================================="
        echo "URL DO WATTSON:"
        echo "$TUNNEL_URL"
        echo "================================="
        echo ""
    fi
done
