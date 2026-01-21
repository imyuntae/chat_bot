# 배포 가이드

이 문서는 챗봇 애플리케이션을 외부에서 접속 가능하도록 배포하는 방법을 설명합니다.

## 배포 옵션

### 1. Streamlit Cloud (추천 - 가장 간단)

Streamlit Cloud는 무료로 Streamlit 앱을 배포할 수 있는 공식 서비스입니다.

#### 준비 사항
1. GitHub 계정
2. Streamlit Cloud 계정 (GitHub로 로그인)

#### 배포 단계

1. **GitHub에 코드 업로드**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

2. **Streamlit Cloud에 배포**
   - https://share.streamlit.io 접속
   - "New app" 클릭
   - GitHub 저장소 선택
   - Main file path: `app.py`
   - Advanced settings에서 Secrets 추가:
     ```
     GEMINI_API_KEY=your-gemini-api-key
     TAVILY_API_KEY=your-tavily-api-key
     GEMINI_MODEL=gemini-2.5-flash
     ```
   - "Deploy" 클릭

3. **배포 완료 후 URL 확인**
   - `https://your-app-name.streamlit.app` 형태의 URL이 생성됩니다.

#### 주의사항
- `.env` 파일은 GitHub에 업로드하지 마세요 (`.gitignore`에 추가)
- API 키는 Streamlit Cloud의 Secrets에만 저장하세요
- `electronics_data.csv` 파일도 GitHub에 업로드해야 합니다

---

### 2. ngrok (로컬 서버를 임시로 외부에 노출)

로컬에서 실행 중인 서버를 임시로 외부에 노출하는 방법입니다.

#### 설치
```bash
# macOS
brew install ngrok

# 또는 https://ngrok.com/download 에서 다운로드
```

#### 사용 방법

1. **Streamlit 서버 실행 (외부 접근 허용)**
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

2. **ngrok 터널 생성**
   ```bash
   ngrok http 8501
   ```

3. **생성된 URL 사용**
   - ngrok이 `https://xxxx-xx-xx-xx-xx.ngrok-free.app` 형태의 URL을 제공합니다
   - 이 URL을 `danawa-demo.html`의 iframe src에 사용하세요

#### 주의사항
- 무료 버전은 세션이 종료되면 URL이 변경됩니다
- HTTPS가 자동으로 제공됩니다
- 일시적인 테스트/데모용으로 적합합니다

---

### 3. 클라우드 서버 (AWS, GCP, Azure 등)

영구적인 배포를 원하는 경우 클라우드 서버를 사용할 수 있습니다.

#### AWS EC2 예시

1. **EC2 인스턴스 생성**
   - Ubuntu 22.04 LTS 선택
   - 보안 그룹에서 포트 8501 열기

2. **서버 설정**
   ```bash
   # SSH 접속
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Python 및 필수 패키지 설치
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # 프로젝트 클론
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   
   # 가상환경 생성 및 패키지 설치
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # .env 파일 생성
   nano .env
   # GEMINI_API_KEY, TAVILY_API_KEY 등 입력
   
   # Streamlit 실행 (백그라운드)
   nohup streamlit run app.py --server.address 0.0.0.0 --server.port 8501 &
   ```

3. **도메인 연결 (선택사항)**
   - Route 53 또는 다른 DNS 서비스 사용
   - Nginx를 리버스 프록시로 사용하여 HTTPS 설정

---

### 4. Railway / Render (간단한 클라우드 배포)

Railway나 Render는 GitHub와 연동하여 쉽게 배포할 수 있습니다.

#### Railway 배포

1. **Railway 계정 생성** (https://railway.app)
2. **GitHub 저장소 연결**
3. **환경 변수 설정**
   - GEMINI_API_KEY
   - TAVILY_API_KEY
   - GEMINI_MODEL
4. **배포 설정**
   - Start Command: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`
   - Port: Railway가 자동 할당

---

## danawa-demo.html 업데이트

배포 후 `danawa-demo.html`의 iframe src를 업데이트해야 합니다:

```html
<!-- 로컬 개발용 -->
<iframe src="http://localhost:8501"></iframe>

<!-- 배포 후 (Streamlit Cloud 예시) -->
<iframe src="https://your-app-name.streamlit.app"></iframe>

<!-- 배포 후 (ngrok 예시) -->
<iframe src="https://xxxx-xx-xx-xx-xx.ngrok-free.app"></iframe>
```

---

## 보안 주의사항

1. **API 키 보호**
   - `.env` 파일을 `.gitignore`에 추가
   - GitHub에 API 키를 직접 커밋하지 마세요
   - 배포 플랫폼의 Secrets/Environment Variables 사용

2. **CORS 설정**
   - Streamlit은 기본적으로 모든 도메인에서 접근 가능합니다
   - 필요시 `config.toml`에서 CORS 설정 조정

3. **HTTPS 사용**
   - 프로덕션 환경에서는 반드시 HTTPS를 사용하세요
   - Streamlit Cloud, ngrok은 자동으로 HTTPS 제공

---

## 문제 해결

### 포트가 열리지 않는 경우
- 방화벽 설정 확인
- 클라우드 서버의 보안 그룹에서 포트 열기

### API 키 오류
- 환경 변수가 제대로 설정되었는지 확인
- `.env` 파일이 올바른 위치에 있는지 확인

### CSV 파일을 찾을 수 없는 경우
- `electronics_data.csv` 파일이 프로젝트 루트에 있는지 확인
- GitHub에 업로드되었는지 확인
