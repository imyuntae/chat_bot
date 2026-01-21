# 빠른 시작 가이드

## 🚀 가장 빠른 배포 방법 (ngrok 사용)

### 1단계: ngrok 설치
```bash
# macOS
brew install ngrok

# 또는 https://ngrok.com/download 에서 다운로드
```

### 2단계: 배포 스크립트 실행
```bash
./deploy-ngrok.sh
```

### 3단계: 생성된 URL 사용
- ngrok이 생성한 HTTPS URL을 복사 (예: `https://xxxx-xx-xx-xx-xx.ngrok-free.app`)
- `danawa-demo.html`을 열 때 URL 파라미터 추가:
  ```
  http://localhost:8000/danawa-demo.html?streamlit_url=https://xxxx-xx-xx-xx-xx.ngrok-free.app
  ```

---

## 🌐 Streamlit Cloud 배포 (영구적)

### 1단계: GitHub에 코드 업로드
```bash
# .gitignore 확인 (API 키가 포함되지 않도록)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

### 2단계: Streamlit Cloud 배포
1. https://share.streamlit.io 접속
2. "New app" 클릭
3. GitHub 저장소 선택
4. Main file path: `app.py`
5. Advanced settings → Secrets 추가:
   ```
   GEMINI_API_KEY=your-gemini-api-key
   TAVILY_API_KEY=your-tavily-api-key
   GEMINI_MODEL=gemini-2.5-flash
   ```
6. "Deploy" 클릭

### 3단계: 배포 URL 사용
- 생성된 URL (예: `https://your-app-name.streamlit.app`)
- `danawa-demo.html`을 열 때:
  ```
  http://localhost:8000/danawa-demo.html?streamlit_url=https://your-app-name.streamlit.app
  ```

---

## 📝 로컬 테스트

### Streamlit 서버 실행
```bash
# 외부 접근 허용
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false ./venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### 데모 페이지 실행
```bash
# 다른 터미널에서
python3 -m http.server 8000
```

### 접속
- 로컬: http://localhost:8000/danawa-demo.html
- 외부 (같은 네트워크): http://your-local-ip:8000/danawa-demo.html

---

## ⚙️ 환경 변수 설정

`.env` 파일 생성:
```bash
GEMINI_API_KEY=your-gemini-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here
GEMINI_MODEL=gemini-2.5-flash
```

---

## 🔧 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# 다른 포트 사용
streamlit run app.py --server.address 0.0.0.0 --server.port 8502
```

### API 키 오류
- `.env` 파일이 프로젝트 루트에 있는지 확인
- 환경 변수가 올바르게 설정되었는지 확인

### CSV 파일 오류
- `electronics_data.csv` 파일이 프로젝트 루트에 있는지 확인
