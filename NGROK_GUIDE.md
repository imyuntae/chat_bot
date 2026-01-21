# ngrok 배포 가이드

## 1단계: ngrok 설치

### macOS (Homebrew)
```bash
brew install ngrok/ngrok/ngrok
```

또는 직접 다운로드:
- https://ngrok.com/download 에서 다운로드
- 압축 해제 후 실행 파일을 PATH에 추가

### ngrok 계정 생성 (선택사항)
무료 계정을 만들면 더 안정적인 URL을 받을 수 있습니다:
1. https://dashboard.ngrok.com/signup 에서 계정 생성
2. 인증 토큰 받기: https://dashboard.ngrok.com/get-started/your-authtoken
3. 토큰 설정:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

## 2단계: Streamlit 서버 확인

Streamlit 서버가 실행 중인지 확인:
```bash
curl http://localhost:8501
```

실행 중이 아니면:
```bash
cd /Users/yuntae/MAS/CT
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false ./venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 3단계: ngrok 실행

새 터미널 창에서:
```bash
ngrok http 8501
```

또는 더 안정적인 URL을 원하면:
```bash
ngrok http 8501 --domain=your-domain.ngrok-free.app
```

## 4단계: 생성된 URL 사용

ngrok이 다음과 같은 정보를 표시합니다:

```
Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8501
```

이 HTTPS URL을 복사하세요!

## 5단계: danawa-demo.html 업데이트

생성된 ngrok URL을 사용하여 데모 페이지 열기:

```bash
# HTTP 서버 실행 (다른 터미널)
cd /Users/yuntae/MAS/CT
python3 -m http.server 8000
```

브라우저에서 접속:
```
http://localhost:8000/danawa-demo.html?streamlit_url=https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

또는 `danawa-demo.html` 파일을 직접 열고, 개발자 도구 콘솔에서:
```javascript
document.getElementById('chatbot-iframe').src = 'https://xxxx-xx-xx-xx-xx.ngrok-free.app';
```

## 자동화 스크립트 사용

`deploy-ngrok.sh` 스크립트를 사용할 수도 있습니다:
```bash
chmod +x deploy-ngrok.sh
./deploy-ngrok.sh
```

## 주의사항

1. **무료 버전 제한**
   - 세션이 종료되면 URL이 변경됩니다
   - 세션 시간 제한이 있을 수 있습니다

2. **ngrok 경고 페이지**
   - 무료 버전은 첫 방문 시 경고 페이지가 표시될 수 있습니다
   - "Visit Site" 버튼을 클릭하면 계속 진행됩니다

3. **HTTPS 자동 제공**
   - ngrok은 자동으로 HTTPS를 제공합니다
   - 별도의 SSL 인증서 설정이 필요 없습니다

## 문제 해결

### 포트가 이미 사용 중
```bash
# 다른 포트 사용
ngrok http 8502
```

### ngrok이 실행되지 않음
- ngrok이 PATH에 있는지 확인: `which ngrok`
- 실행 권한 확인: `chmod +x /path/to/ngrok`

### 연결 오류
- Streamlit 서버가 실행 중인지 확인
- 방화벽 설정 확인
