#!/bin/bash
# Deploy da SELIX API no Google Cloud Platform

# Configurações
INSTANCE_NAME="selix-vm"
ZONE="us-central1-a"
MACHINE_TYPE="e2-micro"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
BOOT_DISK_SIZE="30GB"

echo "=========================================="
echo "Deploy da SELIX API na GCP"
echo "=========================================="

# Verificar se a VM já existe
if gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &>/dev/null; then
    echo "⚠️  VM $INSTANCE_NAME já existe. Atualizando..."
    gcloud compute instances reset $INSTANCE_NAME --zone=$ZONE
else
    echo "🚀 Criando VM $INSTANCE_NAME..."
    gcloud compute instances create $INSTANCE_NAME \
        --machine-type=$MACHINE_TYPE \
        --zone=$ZONE \
        --image-family=$IMAGE_FAMILY \
        --image-project=$IMAGE_PROJECT \
        --boot-disk-size=$BOOT_DISK_SIZE \
        --metadata-from-file=startup-script=scripts/gcp_startup.sh \
        --tags=http-server,https-server
fi

# Abrir porta 5001
echo "🔓 Abrindo porta 5001..."
gcloud compute firewall-rules create selix-api-port \
    --allow=tcp:5001 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server \
    --description="SELIX API port" 2>/dev/null || echo "Regra já existe"

# Obter IP externo
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo ""
echo "=========================================="
echo "✅ Deploy concluído!"
echo "   IP Externo: $EXTERNAL_IP"
echo "   API URL: http://$EXTERNAL_IP:5001"
echo "   Health: http://$EXTERNAL_IP:5001/health"
echo "=========================================="
