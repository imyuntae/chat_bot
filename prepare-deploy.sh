#!/bin/bash
# Streamlit Cloud 배포 준비 스크립트

echo "🚀 Streamlit Cloud 배포 준비 시작..."

# 필수 파일 확인
echo "📋 필수 파일 확인 중..."

files=("app.py" "requirements.txt" "electronics_data.csv")
missing_files=()

for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ 다음 파일들이 없습니다:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "✅ 모든 필수 파일이 있습니다"

# .gitignore 확인
echo ""
echo "🔒 .gitignore 확인 중..."
if grep -q "\.env" .gitignore 2>/dev/null; then
    echo "✅ .env 파일이 .gitignore에 포함되어 있습니다"
else
    echo "⚠️  .env 파일이 .gitignore에 없습니다. 추가하는 것을 권장합니다."
fi

# Git 상태 확인
echo ""
echo "📦 Git 상태 확인 중..."
if [ -d ".git" ]; then
    echo "✅ Git 저장소가 초기화되어 있습니다"
    
    # 커밋되지 않은 변경사항 확인
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  커밋되지 않은 변경사항이 있습니다:"
        git status --short
        echo ""
        read -p "지금 커밋하시겠습니까? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            read -p "커밋 메시지를 입력하세요: " commit_msg
            git commit -m "${commit_msg:-Update for deployment}"
            echo "✅ 커밋 완료"
        fi
    else
        echo "✅ 모든 변경사항이 커밋되었습니다"
    fi
    
    # 원격 저장소 확인
    if git remote -v | grep -q "origin"; then
        echo "✅ 원격 저장소가 설정되어 있습니다:"
        git remote -v | grep origin
    else
        echo "⚠️  원격 저장소가 설정되지 않았습니다"
        echo "다음 명령어로 원격 저장소를 추가하세요:"
        echo "  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    fi
else
    echo "⚠️  Git 저장소가 초기화되지 않았습니다"
    echo "다음 명령어로 초기화하세요:"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
fi

# requirements.txt 확인
echo ""
echo "📦 requirements.txt 확인 중..."
if grep -q "streamlit" requirements.txt && grep -q "google-generativeai" requirements.txt && grep -q "tavily-python" requirements.txt; then
    echo "✅ 필수 패키지가 requirements.txt에 포함되어 있습니다"
else
    echo "⚠️  일부 필수 패키지가 누락되었을 수 있습니다"
fi

# 최종 체크리스트
echo ""
echo "📝 배포 체크리스트:"
echo "  [ ] GitHub 저장소 생성 및 코드 푸시"
echo "  [ ] Streamlit Cloud (https://share.streamlit.io) 접속"
echo "  [ ] 새 앱 생성 및 저장소 연결"
echo "  [ ] Secrets에 API 키 설정:"
echo "      - GEMINI_API_KEY"
echo "      - TAVILY_API_KEY"
echo "      - GEMINI_MODEL (선택사항)"
echo "  [ ] 배포 완료 후 URL 확인"
echo "  [ ] danawa-demo.html에 Streamlit Cloud URL 설정"
echo ""
echo "✅ 준비 완료!"
echo ""
echo "📖 자세한 가이드는 STREAMLIT_CLOUD_DEPLOY.md를 참고하세요"
