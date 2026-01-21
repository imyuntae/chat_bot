#!/bin/bash
# 배포 스크립트 - 클라우드 서버에서 사용

echo "🚀 챗봇 애플리케이션 배포 시작..."

# 가상환경 생성
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 패키지 설치
echo "📥 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. 환경 변수를 설정해주세요."
    echo "필요한 환경 변수:"
    echo "  - GEMINI_API_KEY"
    echo "  - TAVILY_API_KEY"
    echo "  - GEMINI_MODEL (선택사항, 기본값: gemini-2.5-flash)"
fi

# CSV 파일 확인
if [ ! -f "electronics_data.csv" ]; then
    echo "⚠️  electronics_data.csv 파일이 없습니다."
fi

echo "✅ 배포 준비 완료!"
echo ""
echo "애플리케이션 실행:"
echo "  streamlit run app.py --server.address 0.0.0.0 --server.port 8501"
