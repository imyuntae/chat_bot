# GitHub 푸시 단계별 가이드

터미널에서 다음 명령어를 **순서대로** 실행하세요:

## 1단계: 디렉토리 이동
```bash
cd /Users/yuntae/MAS/CT
```

## 2단계: Git 초기화
```bash
git init
```

## 3단계: 원격 저장소 추가
```bash
git remote add origin https://github.com/imyuntae/chat_bot.git
```

이미 추가되어 있다면:
```bash
git remote set-url origin https://github.com/imyuntae/chat_bot.git
```

## 4단계: 모든 파일 추가
```bash
git add .
```

## 5단계: 커밋
```bash
git commit -m "Initial commit: Tech shopping chatbot"
```

## 6단계: 브랜치 이름 변경
```bash
git branch -M main
```

## 7단계: GitHub에 푸시
```bash
git push -u origin main
```

**인증 요청 시:**
- Username: `imyuntae`
- Password: **Personal Access Token** 입력 (비밀번호가 아님!)

---

## 문제 해결

### 저장소가 이미 다른 내용으로 초기화된 경우
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### 원격 저장소 확인
```bash
git remote -v
```

### 현재 상태 확인
```bash
git status
```
