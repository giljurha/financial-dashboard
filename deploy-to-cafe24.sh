#!/bin/bash

# Cafe24 서버 배포 스크립트
SERVER_IP="1.234.75.247"
SERVER_USER="root"
PROJECT_DIR="/root/financial-dashboard"

echo "=== Cafe24 서버에 배포 시작 ==="

# SSH로 서버 설정 및 배포
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "Docker 설치 중..."

    # 우분투 Docker 설치
    apt-get update
    apt-get install -y ca-certificates curl gnupg lsb-release

    # Docker GPG 키 추가
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Docker 저장소 추가
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Docker 설치
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo "Docker 설치 완료"
else
    echo "Docker가 이미 설치되어 있습니다"
fi

# Docker Compose 확인
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose 설치 중..."
    curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose 설치 완료"
fi

# Git 설치 확인
if ! command -v git &> /dev/null; then
    echo "Git 설치 중..."
    apt-get install -y git
fi

# 프로젝트 디렉토리 생성 및 이동
mkdir -p /root/financial-dashboard
cd /root/financial-dashboard

# Git 저장소 클론 또는 업데이트
if [ -d ".git" ]; then
    echo "기존 저장소 업데이트 중..."
    git pull origin main
else
    echo "저장소 클론 중..."
    git clone https://github.com/giljurha/financial-dashboard.git .
fi

# Docker 이미지 빌드 및 실행
echo "Docker 컨테이너 시작 중..."
docker-compose down
docker-compose up -d --build

# 상태 확인
docker-compose ps

echo "=== 배포 완료 ==="
echo "Frontend: http://giljurha01.cafe24.com:3000"
echo "Backend: http://giljurha01.cafe24.com:8080"

ENDSSH

echo "=== 배포 스크립트 실행 완료 ==="
