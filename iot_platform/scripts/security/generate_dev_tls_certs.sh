#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CERT_DIR="$BASE_DIR/backend_server/mosquitto/config/certs"

mkdir -p "$CERT_DIR"

CA_KEY="$CERT_DIR/ca.key"
CA_CRT="$CERT_DIR/ca.crt"
SERVER_KEY="$CERT_DIR/server.key"
SERVER_CSR="$CERT_DIR/server.csr"
SERVER_CRT="$CERT_DIR/server.crt"
EXT_FILE="$CERT_DIR/server.ext"

echo "[1/5] Generating CA..."
openssl genrsa -out "$CA_KEY" 4096
openssl req -x509 -new -nodes \
  -key "$CA_KEY" \
  -sha256 \
  -days 3650 \
  -out "$CA_CRT" \
  -subj "/CN=IndustrialIoT-Dev-CA"

echo "[2/5] Generating server key..."
openssl genrsa -out "$SERVER_KEY" 2048

echo "[3/5] Generating server CSR..."
openssl req -new \
  -key "$SERVER_KEY" \
  -out "$SERVER_CSR" \
  -subj "/CN=mosquitto"

echo "[4/5] Creating SAN extension..."
cat > "$EXT_FILE" <<EOF
subjectAltName=DNS:mosquitto,DNS:localhost,DNS:host.docker.internal,IP:127.0.0.1
extendedKeyUsage=serverAuth
EOF

echo "[5/5] Signing server certificate..."
openssl x509 -req \
  -in "$SERVER_CSR" \
  -CA "$CA_CRT" \
  -CAkey "$CA_KEY" \
  -CAcreateserial \
  -out "$SERVER_CRT" \
  -days 825 \
  -sha256 \
  -extfile "$EXT_FILE"

rm -f "$SERVER_CSR" "$EXT_FILE"

chmod 0644 "$CA_CRT" "$SERVER_CRT" "$SERVER_KEY"
chmod 0600 "$CA_KEY

echo "[OK] TLS certificates generated in $CERT_DIR"
echo "[OK] Mosquitto files:"
echo "     $CERT_DIR/ca.crt"
echo "     $CERT_DIR/server.crt"
echo "     $CERT_DIR/server.key"