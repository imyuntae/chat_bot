#!/bin/bash
# 1단계: GitHub 저장소 생성 및 코드 업로드

echo "🚀 1단계: GitHub 저장소 생성 및 코드 업로드"
echo ""

# 현재 디렉토리 확인
cd "$(dirname "$0")"
echo "📁 작업 디렉토리: $(pwd)"
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

# .gitignore 확인
echo "2️⃣ .gitignore 확인 중..."
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore; then
        echo "   ✅ .env 파일이 .gitignore에 포함되어 있습니다 (안전)"
    else
        echo "   ⚠️  .env 파일이 .gitignore에 없습니다"
    fi
else
    echo "   ⚠️  .gitignore 파일이 없습니다"
fi
echo ""

# 파일 추가
echo "3️⃣ 파일 추가 중..."
git add .
echo "   ✅ 모든 파일이 스테이징되었습니다"
echo ""

# 커밋
echo "4️⃣ 커밋 생성 중..."
read -p "   커밋 메시지를 입력하세요 (기본값: Initial commit): " commit_msg
commit_msg=${commit_msg:-"Initial commit: Tech shopping chatbot"}
git commit -m "$commit_msg"
echo "   ✅ 커밋 완료: $commit_msg"
echo ""

# 원격 저장소 확인
echo "5️⃣ 원격 저장소 확인 중..."
if git remote -v | grep -q "origin"; then
    echo "   ✅ 원격 저장소가 이미 설정되어 있습니다:"
    git remote -v | grep origin
    echo ""
    read -p "   기존 원격 저장소를 사용하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
        echo "   ✅ 기존 원격 저장소 제거됨"
    fi
fi

if ! git remote -v | grep -q "origin"; then
    echo ""
    echo "6️⃣ 원격 저장소 설정"
    echo "   먼저 GitHub에서 새 저장소를 생성하세요:"
    echo "   https://github.com/new"
    echo ""
    read -p "   GitHub 저장소 URL을 입력하세요 (예: https://github.com/username/repo.git): " repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "   ✅ 원격 저장소 추가됨: $repo_url"
    else
        echo "   ⚠️  저장소 URL이 입력되지 않았습니다"
        echo "   나중에 다음 명령어로 추가하세요:"
        echo "   git remote add origin https://github.com/username/repo.git"
    fi
fi
echo ""

# 브랜치 이름 변경
echo "7️⃣ 브랜치 이름을 main으로 변경 중..."
git branch -M main
echo "   ✅ 브랜치 이름 변경 완료"
echo ""

# 푸시
echo "8️⃣ GitHub에 푸시 중..."
if git remote -v | grep -q "origin"; then
    read -p "   지금 푸시하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin main
        echo ""
        echo "   ✅ 푸시 완료!"
        echo ""
        echo "🎉 1단계 완료!"
        echo ""
        echo "다음 단계:"
        echo "   1. https://share.streamlit.io 접속"
        echo "   2. GitHub 계정으로 로그인"
        echo "   3. 'New app' 클릭"
        echo "   4. 방금 만든 저장소 선택"
        echo "   5. Main file path: app.py"
        echo "   6. Advanced settings → Secrets에 API 키 추가"
        echo "   7. Deploy 클릭"
    else
        echo "   나중에 다음 명령어로 푸시하세요:"
        echo "   git push -u origin main"
    fi
else
    echo "   ⚠️  원격 저장소가 설정되지 않아 푸시할 수 없습니다"
    echo "   먼저 원격 저장소를 추가하세요"
fi
echo ""

echo "📝 현재 상태:"
echo "   - Git 저장소: ✅ 초기화됨"
echo "   - 커밋: ✅ 완료"
if git remote -v | grep -q "origin"; then
    echo "   - 원격 저장소: ✅ 설정됨"
    echo "   - 푸시: $(git log origin/main..HEAD 2>/dev/null | wc -l | tr -d ' ')개의 커밋이 푸시 대기 중"
else
    echo "   - 원격 저장소: ⚠️  설정 필요"
fi
