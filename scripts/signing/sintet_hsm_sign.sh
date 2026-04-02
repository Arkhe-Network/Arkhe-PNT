#!/bin/bash
# SINTET Cluster - Internal HSM Image Signing Simulation
# Utiliza chaves locais geradas pelo HSM interno para assinar imagens do cluster SINTET.

set -e

echo "🜏 [SINTET HSM] Inicializando módulo de segurança de hardware..."

KEY_DIR="../../certs/sintet_hsm"
mkdir -p "$KEY_DIR"

if [ ! -f "$KEY_DIR/sintet_hsm_private.pem" ]; then
    echo "🜏 [SINTET HSM] Gerando par de chaves ECDSA (secp384r1) no enclave seguro..."
    openssl ecparam -name secp384r1 -genkey -noout -out "$KEY_DIR/sintet_hsm_private.pem"
    openssl ec -in "$KEY_DIR/sintet_hsm_private.pem" -pubout -out "$KEY_DIR/sintet_hsm_public.pem"
    echo "🜏 [SINTET HSM] Chaves geradas com sucesso."
else
    echo "🜏 [SINTET HSM] Chaves locais encontradas."
fi

IMAGE=$1

if [ -z "$IMAGE" ]; then
    echo "Uso: $0 <imagem_docker>"
    exit 1
fi

echo "🜏 [SINTET HSM] Calculando SHA256 da imagem $IMAGE..."
# Simula a extração do digest da imagem
IMAGE_DIGEST=$(echo -n "$IMAGE" | sha256sum | awk '{print $1}')

echo "🜏 [SINTET HSM] Assinando digest $IMAGE_DIGEST com chave privada do HSM..."
SIGNATURE=$(echo -n "$IMAGE_DIGEST" | openssl dgst -sha256 -sign "$KEY_DIR/sintet_hsm_private.pem" | base64 -w 0)

echo "🜏 [SINTET HSM] Assinatura gerada: $SIGNATURE"
echo "🜏 [SINTET HSM] Anexando assinatura à imagem no registry interno..."

# Simula o push da assinatura para o registry (ex: Cosign format)
cat <<EOF > "$KEY_DIR/${IMAGE_DIGEST}.sig"
{
  "image": "$IMAGE",
  "digest": "$IMAGE_DIGEST",
  "signature": "$SIGNATURE",
  "signer": "SINTET-INTERNAL-HSM-01"
}
EOF

echo "🜏 [SINTET HSM] Boot seguro preparado para $IMAGE. Apenas o Admission Controller SINTET poderá autorizar a execução."
