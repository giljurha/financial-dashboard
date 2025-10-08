#!/bin/bash

# nginx 로그 확인 스크립트
SERVER_IP="1.234.75.247"
SERVER_USER="root"

echo "=== Nginx 로그 확인 ==="

ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'

cd /root/financial-dashboard

echo "=== Nginx 로그 (최근 100줄) ==="
docker-compose logs --tail=100 nginx

ENDSSH
