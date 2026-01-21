#!/bin/bash
# GitHub 저장소 연결 및 푸시 스크립트

echo "🚀 GitHub 저장소 연결 및 푸시"
echo ""

cd "$(dirname "$0")"

# GitHub 사용자명 입력
read -p "GitHub 사용자명을 입력하세요: " github_username

if [ -z "$github_username" ]; then
    echo "❌ 사용자명이 입력되지 않았습니다"
    exit 1
fi

repo_name="chat_bot"
repo_url="https://github.com/${github_username}/${repo_name}.git"

echo ""
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
    echo "   ⚠️  이미 원격 저장소가 설정되어 있습니다"
    git remote remove origin
    echo "   ✅ 기존 원격 저장소 제거됨"
fi

git remote add origin "$repo_url"
echo "   ✅ 원격 저장소 추가됨: $repo_url"
echo ""

# 파일 추가
echo "3️⃣ 파일 추가 중..."
git add .
echo "   ✅ 모든 파일이 스테이징되었습니다"
echo ""

# 커밋
echo "4️⃣ 커밋 생성 중..."
git commit -m "Initial commit: Tech shopping chatbot" || {
    echo "   ⚠️  커밋할 변경사항이 없거나 이미 커밋되었습니다"
}
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
    echo "다음 단계:"
    echo "   1. https://share.streamlit.io 접속"
    echo "   2. GitHub 계정으로 로그인"
    echo "   3. 'New app' 클릭"
    echo "   4. '$repo_name' 저장소 선택"
    echo "   5. Main file path: app.py"
    echo "   6. Advanced settings → Secrets에 API 키 추가"
    echo "   7. Deploy 클릭"
else
    echo ""
    echo "❌ 푸시 실패"
    echo ""
    echo "가능한 원인:"
    echo "   - GitHub 인증 필요 (Personal Access Token 필요할 수 있음)"
    echo "   - 저장소 URL이 잘못됨"
    echo "   - 저장소가 이미 다른 내용으로 초기화됨"
    echo ""
    echo "수동으로 푸시하려면:"
    echo "   git push -u origin main"
fi
