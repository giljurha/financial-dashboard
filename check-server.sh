#!/bin/bash

# Cafe24 서버 상태 확인 스크립트
SERVER_IP="1.234.75.247"
SERVER_USER="root"

echo "=== Cafe24 서버 상태 확인 ==="

ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'

cd /root/financial-dashboard

echo "=== Docker 컨테이너 상태 ==="
docker-compose ps

echo ""
echo "=== Backend 로그 (최근 50줄) ==="
docker-compose logs --tail=50 backend

echo ""
echo "=== Frontend 로그 (최근 50줄) ==="
docker-compose logs --tail=50 frontend

ENDSSH
