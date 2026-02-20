# Design QA Checklist Template

이 파일을 복사해서 `docs/design/[version]/qa-checklist.md`로 저장해 사용하세요.

## Visual

- [ ] 폰트/굵기/크기가 시안과 일치
- [ ] 색상 토큰이 시안과 일치
- [ ] 간격(패딩/마진)이 시안과 일치
- [ ] 버튼/입력/칩 상태(default/hover/active/disabled) 반영

## Responsive

- [ ] 360px 모바일에서 레이아웃 깨짐 없음
- [ ] 768px 태블릿에서 의도된 구성 유지
- [ ] 1280px 데스크탑에서 최대 너비/정렬 확인

## Interaction

- [ ] 모달 z-index 정상 (지도/패널보다 위)
- [ ] 클릭 타겟 최소 크기 확보
- [ ] 로딩/에러/빈 상태 표시

## Data

- [ ] API 필드명과 화면 바인딩 일치
- [ ] null/빈 값 fallback 처리
- [ ] 정렬/필터 파라미터 반영

## Admin (if applicable)

- [ ] 매핑 행 추가/삭제 동작
- [ ] 핀 좌표 입력/수정 동작
- [ ] 펼침(details)에서 매핑 행 정보 확인 가능
- [ ] 저장 후 목록 즉시 반영

## Release Check

- [ ] 빌드 통과
- [ ] 핵심 시나리오 수동 테스트 완료
- [ ] PR 설명에 시안 버전/경로 링크 기재
