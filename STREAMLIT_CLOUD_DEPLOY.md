# Streamlit Cloud 배포 가이드

## 📋 사전 준비

### 1. GitHub 계정 및 저장소
- GitHub 계정이 필요합니다
- 새 저장소를 만들거나 기존 저장소를 사용할 수 있습니다

### 2. 필수 파일 확인
다음 파일들이 프로젝트 루트에 있는지 확인하세요:
- ✅ `app.py` - 메인 애플리케이션
- ✅ `requirements.txt` - Python 패키지 목록
- ✅ `electronics_data.csv` - 상품 데이터 (GitHub에 업로드 필요)
- ✅ `.gitignore` - Git 제외 파일 목록
- ✅ `.streamlit/config.toml` - Streamlit 설정 (선택사항)

## 🚀 배포 단계

### 1단계: GitHub 저장소 준비

#### 새 저장소 생성
1. https://github.com/new 에서 새 저장소 생성
2. 저장소 이름 입력 (예: `tech-shopping-chatbot`)
3. Public 또는 Private 선택
4. "Create repository" 클릭

#### 로컬 코드 업로드

```bash
cd /Users/yuntae/MAS/CT

# Git 초기화 (아직 안 했다면)
git init

# .gitignore 확인 (API 키가 포함되지 않도록)
cat .gitignore

# 모든 파일 추가 (electronics_data.csv 포함)
git add .

# 커밋
git commit -m "Initial commit: Tech shopping chatbot"

# GitHub 저장소 연결 (YOUR_USERNAME과 YOUR_REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 또는 SSH 사용
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git

# 코드 푸시
git branch -M main
git push -u origin main
```

**⚠️ 중요: `.env` 파일은 절대 커밋하지 마세요!**
- `.gitignore`에 이미 포함되어 있어야 합니다
- API 키는 Streamlit Cloud의 Secrets에만 저장합니다

### 2단계: Streamlit Cloud 배포

1. **Streamlit Cloud 접속**
   - https://share.streamlit.io 접속
   - GitHub 계정으로 로그인

2. **새 앱 생성**
   - "New app" 버튼 클릭
   - 또는 "Deploy an app" 클릭

3. **저장소 선택**
   - GitHub 저장소 선택
   - Branch: `main` (또는 사용 중인 브랜치)
   - Main file path: `app.py`

4. **고급 설정 (Advanced settings)**
   - "Advanced settings" 클릭
   - Secrets 섹션에서 다음 환경 변수 추가:

   ```
   GEMINI_API_KEY=your-gemini-api-key-here
   TAVILY_API_KEY=your-tavily-api-key-here
   GEMINI_MODEL=gemini-2.5-flash
   ```

   **Secrets 형식:**
   ```
   GEMINI_API_KEY = "your-actual-api-key"
   TAVILY_API_KEY = "your-actual-api-key"
   GEMINI_MODEL = "gemini-2.5-flash"
   ```

5. **배포 시작**
   - "Deploy" 버튼 클릭
   - 배포가 완료될 때까지 대기 (보통 1-2분)

### 3단계: 배포 확인

배포가 완료되면 다음과 같은 URL이 생성됩니다:
```
https://your-app-name.streamlit.app
```

또는
```
https://YOUR_USERNAME-YOUR_REPO_NAME.streamlit.app
```

브라우저에서 이 URL로 접속하여 챗봇이 정상 작동하는지 확인하세요.

### 4단계: danawa-demo.html 업데이트

배포된 Streamlit Cloud URL을 사용하여 데모 페이지 업데이트:

**방법 1: URL 파라미터 사용 (권장)**
```
http://localhost:8000/danawa-demo.html?streamlit_url=https://your-app-name.streamlit.app
```

**방법 2: danawa-demo.html 파일 직접 수정**
```html
<iframe 
    id="chatbot-iframe"
    src="https://your-app-name.streamlit.app"
    title="테크 전문 쇼핑 가이드 챗봇"
></iframe>
```

## 🔧 문제 해결

### 배포 실패

**원인 1: requirements.txt 오류**
- `requirements.txt`에 모든 필수 패키지가 포함되어 있는지 확인
- 패키지 버전 호환성 확인

**원인 2: CSV 파일 누락**
- `electronics_data.csv` 파일이 GitHub에 업로드되었는지 확인
- 파일 크기가 너무 크면 (100MB 이상) 문제가 될 수 있습니다

**원인 3: API 키 오류**
- Streamlit Cloud의 Secrets에 API 키가 올바르게 설정되었는지 확인
- Secrets 형식이 올바른지 확인 (따옴표 사용)

### 로그 확인

Streamlit Cloud 대시보드에서:
1. 앱 선택
2. "Manage app" 클릭
3. "Logs" 탭에서 오류 메시지 확인

### 자주 발생하는 오류

**ModuleNotFoundError**
- `requirements.txt`에 누락된 패키지 추가
- 배포 재시도

**FileNotFoundError: electronics_data.csv**
- CSV 파일이 GitHub에 업로드되었는지 확인
- 파일 경로가 올바른지 확인

**API Key Error**
- Secrets에 API 키가 올바르게 설정되었는지 확인
- 환경 변수 이름이 정확한지 확인 (대소문자 구분)

## 📝 업데이트 방법

코드를 수정한 후:

```bash
git add .
git commit -m "Update: 설명"
git push origin main
```

Streamlit Cloud는 자동으로 변경사항을 감지하고 재배포합니다.

## 🔒 보안 주의사항

1. **API 키 보호**
   - `.env` 파일을 절대 GitHub에 커밋하지 마세요
   - Streamlit Cloud Secrets에만 저장하세요

2. **CSV 파일**
   - 민감한 정보가 포함되어 있다면 `.gitignore`에 추가
   - 현재는 공개 데이터이므로 문제없습니다

3. **공개 저장소**
   - Public 저장소를 사용하면 코드가 공개됩니다
   - API 키는 Secrets에 저장되므로 안전합니다

## 🎉 완료!

배포가 완료되면:
- ✅ Streamlit Cloud URL로 챗봇 접속 가능
- ✅ 전 세계 어디서나 접속 가능
- ✅ HTTPS 자동 제공
- ✅ 자동 재배포 (GitHub push 시)

## 다음 단계

1. `danawa-demo.html`을 실제 웹사이트에 배포
2. Streamlit Cloud URL을 iframe src에 사용
3. 테스트 및 최적화
