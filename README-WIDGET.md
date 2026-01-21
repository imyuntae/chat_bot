# 채널톡 스타일 챗봇 위젯 사용 가이드

## 개요
이 챗봇을 웹사이트에 채널톡처럼 임베드할 수 있습니다.

## 방법 1: HTML 파일 사용 (테스트용)

1. `chatbot-widget.html` 파일을 브라우저에서 열거나
2. 웹사이트에 iframe으로 임베드:

```html
<iframe src="chatbot-widget.html" width="400" height="600" frameborder="0"></iframe>
```

## 방법 2: JavaScript 스크립트 임베드 (권장)

웹사이트의 `</body>` 태그 직전에 다음 코드를 추가하세요:

```html
<script 
    src="https://your-domain.com/embed-script.js"
    data-streamlit-url="http://localhost:8501"
    data-button-color="#6336FF"
    data-position="bottom-right"
></script>
```

### 설정 옵션

- `data-streamlit-url`: Streamlit 서버 주소 (필수)
- `data-button-color`: 버튼 색상 (기본값: #6336FF)
- `data-position`: 버튼 위치 (bottom-right 또는 bottom-left)

## 방법 3: 직접 HTML 코드 삽입

웹사이트 HTML에 직접 코드를 삽입할 수도 있습니다:

```html
<!-- 챗봇 위젯 HTML -->
<div id="channel-chatbot-widget" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
    <div id="chatbot-window" style="display: none; position: absolute; bottom: 80px; right: 0; width: 400px; height: 600px; background: white; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.2);">
        <div style="background: #6336FF; color: white; padding: 16px; display: flex; justify-content: space-between;">
            <h3 style="margin: 0;">💻 테크 전문 쇼핑 가이드</h3>
            <button onclick="document.getElementById('chatbot-window').style.display='none'; document.getElementById('chatbot-button').textContent='💬';">×</button>
        </div>
        <iframe src="http://localhost:8501" style="width: 100%; height: calc(100% - 60px); border: none;"></iframe>
    </div>
    <button id="chatbot-button" onclick="var w=document.getElementById('chatbot-window'); w.style.display=w.style.display==='none'?'flex':'none'; this.textContent=w.style.display==='none'?'💬':'✕';" style="width: 60px; height: 60px; border-radius: 50%; background: #6336FF; color: white; border: none; cursor: pointer; font-size: 24px;">💬</button>
</div>
```

## Streamlit 서버 실행

챗봇이 작동하려면 Streamlit 서버가 실행 중이어야 합니다:

```bash
cd /Users/yuntae/MAS/CT
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false ./venv/bin/python -m streamlit run app.py --server.port 8501
```

## 프로덕션 배포

프로덕션 환경에서는:

1. Streamlit 서버를 안정적으로 호스팅 (예: AWS, GCP, Heroku 등)
2. HTTPS 사용 (보안 및 iframe 호환성)
3. CORS 설정 확인
4. `data-streamlit-url`을 실제 서버 주소로 변경

## 주의사항

- Streamlit 서버가 실행 중이어야 챗봇이 작동합니다
- iframe 보안 정책에 따라 일부 브라우저에서 차단될 수 있습니다
- HTTPS를 사용하는 것이 권장됩니다