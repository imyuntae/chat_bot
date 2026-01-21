#!/bin/bash
# ngrok을 사용한 빠른 배포 스크립트

echo "🚀 ngrok을 사용한 배포 시작..."

# Streamlit 서버가 실행 중인지 확인
if ! pgrep -f "streamlit run app.py" > /dev/null; then
    echo "📡 Streamlit 서버 시작 중..."
    cd "$(dirname "$0")"
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false ./venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 &
    sleep 5
    echo "✅ Streamlit 서버가 시작되었습니다."
else
    echo "✅ Streamlit 서버가 이미 실행 중입니다."
fi

# ngrok이 설치되어 있는지 확인
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok이 설치되어 있지 않습니다."
    echo "설치 방법:"
    echo "  macOS: brew install ngrok"
    echo "  또는 https://ngrok.com/download 에서 다운로드"
    exit 1
fi

# ngrok 실행
echo "🌐 ngrok 터널 생성 중..."
echo ""
echo "⚠️  중요: 생성된 HTTPS URL을 복사하여 danawa-demo.html의 iframe src에 사용하세요!"
echo ""

ngrok http 8501
