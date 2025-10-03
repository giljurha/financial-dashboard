# Financial Dashboard - 프로덕션 배포 가이드

## 🚀 배포 개요

이 프로젝트는 GitHub Actions를 사용한 자동 CI/CD 파이프라인과 Docker를 이용한 컨테이너화된 배포를 지원합니다.

## 📋 사전 요구사항

### 서버 요구사항
- Ubuntu 20.04 LTS 또는 최신 버전
- Docker 및 Docker Compose 설치
- 최소 2GB RAM, 20GB 디스크 공간
- 도메인 연결 (SSL 인증서 발급용)

### GitHub 설정
- GitHub 저장소
- GitHub Actions 활성화
- GitHub Container Registry 접근 권한

## 🔧 초기 설정

### 1. 서버 준비

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 프로젝트 클론
git clone https://github.com/YOUR_USERNAME/financial-dashboard.git
cd financial-dashboard
```

### 2. GitHub Secrets 설정

GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 secrets을 추가:

```
HOST: 서버 IP 주소
USERNAME: 서버 SSH 사용자명
PRIVATE_KEY: SSH 개인 키
PORT: SSH 포트 (기본값: 22)
GITHUB_TOKEN: 자동 생성됨 (수동 설정 불필요)
```

### 3. 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env
vi .env

# 필요한 값들 설정
export GITHUB_REPOSITORY="yourusername/financial-dashboard"
export DOMAIN_NAME="yourdomain.com"
```

## 🚀 배포 프로세스

### 자동 배포 (권장)

1. **main 브랜치에 푸시**:
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

2. **GitHub Actions 워크플로우가 자동으로**:
   - 코드 테스트 실행
   - Docker 이미지 빌드
   - GitHub Container Registry에 이미지 푸시
   - 프로덕션 서버에 자동 배포

### 수동 배포

```bash
# 배포 스크립트 실행 권한 부여
chmod +x scripts/deploy.sh

# 배포 실행
./scripts/deploy.sh
```

## 🔒 SSL 인증서 설정

### Let's Encrypt 자동 설정

```bash
# SSL 설정 스크립트 실행 권한 부여
chmod +x scripts/setup-ssl.sh

# SSL 인증서 발급 및 설정
./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com
```

## 📊 모니터링 및 로그

### 서비스 상태 확인

```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs

# 특정 서비스 로그 확인
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend
docker-compose -f docker-compose.prod.yml logs nginx
```

### 헬스체크

```bash
# 백엔드 헬스체크
curl https://yourdomain.com/actuator/health

# 프론트엔드 접근 확인
curl https://yourdomain.com
```

## 🔄 업데이트 및 롤백

### 업데이트

```bash
# 최신 코드 가져오기
git pull origin main

# 재배포
./scripts/deploy.sh
```

### 롤백

```bash
# 이전 버전으로 롤백
git checkout HEAD~1
./scripts/deploy.sh

# 또는 특정 커밋으로 롤백
git checkout <commit-hash>
./scripts/deploy.sh
```

## 🛠 트러블슈팅

### 일반적인 문제들

1. **포트 충돌**:
   ```bash
   # 포트 사용 중인 프로세스 확인
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :443
   ```

2. **Docker 이미지 문제**:
   ```bash
   # 이미지 강제 재빌드
   docker-compose -f docker-compose.prod.yml build --no-cache

   # 사용하지 않는 이미지 정리
   docker image prune -a
   ```

3. **SSL 인증서 문제**:
   ```bash
   # 인증서 갱신
   docker-compose -f docker-compose.prod.yml run --rm certbot renew

   # nginx 재시작
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

4. **권한 문제**:
   ```bash
   # Docker 권한 설정
   sudo usermod -aG docker $USER
   newgrp docker
   ```

## 📈 성능 최적화

### 리소스 모니터링

```bash
# 시스템 리소스 확인
docker stats

# 디스크 사용량 확인
df -h
docker system df
```

### 로그 로테이션

```bash
# Docker 로그 크기 제한 설정
# docker-compose.prod.yml에 추가:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔧 고급 설정

### 백업 설정

```bash
# 데이터 백업 스크립트 작성
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.prod.yml exec backend pg_dump -U postgres financial_dashboard > backup_$DATE.sql
```

### 모니터링 도구 추가

```bash
# Prometheus + Grafana 설정 (선택사항)
# monitoring/docker-compose.monitoring.yml 파일 생성
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. GitHub Actions 워크플로우 로그
2. 서버의 Docker 컨테이너 로그
3. nginx 에러 로그
4. 시스템 리소스 상태

추가 도움이 필요한 경우 이슈를 생성해 주세요.