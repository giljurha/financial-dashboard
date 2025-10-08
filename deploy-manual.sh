#!/bin/bash

# 수동 배포 가이드
echo "=== Cafe24 서버 배포 가이드 ==="
echo ""
echo "PowerShell에서 다음 명령어를 실행하세요:"
echo ""
echo "ssh root@1.234.75.247"
echo "# 비밀번호: eastside23!"
echo ""
echo "=== 서버 접속 후 실행할 명령어 ==="
cat << 'COMMANDS'

# 1. Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 2. Docker Compose 설치
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. Git 설치
apt-get update && apt-get install -y git

# 4. 프로젝트 클론
cd /root
git clone https://github.com/giljurha/financial-dashboard.git
cd financial-dashboard

# 5. Docker Compose 실행
docker-compose up -d --build

# 6. 상태 확인
docker-compose ps

COMMANDS

echo ""
echo "=== 접속 정보 ==="
echo "Frontend: http://1.234.75.247:3000"
echo "Backend: http://1.234.75.247:8080"
