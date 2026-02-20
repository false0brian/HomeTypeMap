# Repo Split Playbook (Backend / Frontend)

목표:
- 현재 모노레포를 유지한 채 CI를 먼저 분리 운영
- 이후 `backend`, `frontend`를 별도 GitHub 저장소로 분리

## 0. 사전 조건
- main 기준 최신 동기화
- GitHub에 빈 저장소 2개 생성
  - 예: `HomeTypeMap-backend`
  - 예: `HomeTypeMap-frontend`

## 1. 모노레포에서 선행 완료할 항목
- backend CI: `.github/workflows/backend-ci.yml`
- frontend CI: `.github/workflows/frontend-ci.yml`
- API 계약/버전 정책: `docs/api-contract.md`

## 2. 백엔드 저장소 분리
```bash
git checkout main
git pull --ff-only origin main

git subtree split --prefix=app -b split/backend-app
git subtree split --prefix=alembic -b split/backend-alembic
```

권장 방식:
- 실제 분리 시에는 `app`만 분리하지 말고 백엔드 런타임에 필요한 루트 파일까지 새 레포에 포함해 구성
  - `requirements.txt`, `alembic.ini`, `scripts/`, `tests/`
- 이 과정은 새 레포 초기 커밋 구성에서 수동 정리가 더 안전하다.

## 3. 프론트 저장소 분리
```bash
git checkout main
git pull --ff-only origin main

git subtree split --prefix=frontend -b split/frontend
git push git@github.com:<org>/HomeTypeMap-frontend.git split/frontend:main
```

## 4. 권장 마이그레이션 전략
1. 먼저 프론트만 분리 (리스크 낮음)
2. 백엔드는 모노레포 유지하며 안정화
3. 백엔드 분리 후 API contract를 별도 public artifact로 publish

## 5. 분리 후 체크리스트
- 각 저장소의 CI green 확인
- 배포 파이프라인 분리 확인
- 환경변수/시크릿 재등록
- README/문서 링크 상호 참조 업데이트
- 모노레포는 archive 또는 infra-only 레포로 정리
