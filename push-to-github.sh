#!/bin/bash
# GitHub에 코드 푸시 스크립트

echo "🚀 GitHub 저장소에 코드 푸시"
echo ""

cd "$(dirname "$0")"

github_username="imyuntae"
repo_name="chat_bot"
repo_url="https://github.com/${github_username}/${repo_name}.git"

echo "📋 설정 정보:"
echo "   사용자명: $github_username"
echo "   저장소: $repo_name"
echo "   URL: $repo_url"
echo ""

# Git 초기화
echo "1️⃣ Git 저장소 초기화 중..."
if [ -d ".git" ]; then
    echo "   ✅ Git 저장소가 이미 초기화되어 있습니다"
else
    git init
    echo "   ✅ Git 저장소 초기화 완료"
fi
echo ""

# 원격 저장소 설정
echo "2️⃣ 원격 저장소 설정 중..."
if git remote -v | grep -q "origin"; then
    current_url=$(git remote get-url origin 2>/dev/null)
    if [ "$current_url" != "$repo_url" ]; then
        echo "   ⚠️  기존 원격 저장소 URL: $current_url"
        read -p "   새로운 URL로 변경하시겠습니까? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git remote remove origin
            git remote add origin "$repo_url"
            echo "   ✅ 원격 저장소 업데이트됨"
        fi
    else
        echo "   ✅ 원격 저장소가 이미 올바르게 설정되어 있습니다"
    fi
else
    git remote add origin "$repo_url"
    echo "   ✅ 원격 저장소 추가됨"
fi
echo ""

# 파일 추가
echo "3️⃣ 파일 추가 중..."
git add .
echo "   ✅ 모든 파일이 스테이징되었습니다"
echo ""

# 커밋
echo "4️⃣ 커밋 생성 중..."
if [ -n "$(git status --porcelain)" ]; then
    git commit -m "Initial commit: Tech shopping chatbot"
    echo "   ✅ 커밋 완료"
else
    echo "   ℹ️  커밋할 변경사항이 없습니다 (이미 커밋되었을 수 있음)"
fi
echo ""

# 브랜치 이름 변경
echo "5️⃣ 브랜치 이름을 main으로 변경 중..."
git branch -M main
echo "   ✅ 브랜치 이름 변경 완료"
echo ""

# 푸시
echo "6️⃣ GitHub에 푸시 중..."
echo "   (GitHub 인증이 필요할 수 있습니다)"
echo ""
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 성공! 코드가 GitHub에 업로드되었습니다!"
    echo ""
    echo "저장소 URL: https://github.com/${github_username}/${repo_name}"
    echo ""
    echo "다음 단계:"
    echo "   1. https://share.streamlit.io 접속"
    echo "   2. GitHub 계정으로 로그인"
    echo "   3. 'New app' 클릭"
    echo "   4. 'chat_bot' 저장소 선택"
    echo "   5. Main file path: app.py"
    echo "   6. Advanced settings → Secrets에 API 키 추가:"
    echo "      GEMINI_API_KEY = \"your-key\""
    echo "      TAVILY_API_KEY = \"your-key\""
    echo "      GEMINI_MODEL = \"gemini-2.5-flash\""
    echo "   7. Deploy 클릭"
else
    echo ""
    echo "❌ 푸시 실패"
    echo ""
    echo "가능한 원인 및 해결 방법:"
    echo ""
    echo "1. GitHub 인증 필요:"
    echo "   - Personal Access Token 생성: https://github.com/settings/tokens"
    echo "   - 토큰으로 인증: git push -u origin main"
    echo ""
    echo "2. 저장소가 이미 다른 내용으로 초기화됨:"
    echo "   git pull origin main --allow-unrelated-histories"
    echo "   git push -u origin main"
    echo ""
    echo "3. 저장소 URL 확인:"
    echo "   git remote -v"
    echo ""
    echo "수동으로 다시 시도:"
    echo "   git push -u origin main"
fi
