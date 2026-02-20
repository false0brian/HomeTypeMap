# Design Handoff Template

이 폴더는 디자인 시안을 개발로 넘길 때 사용하는 표준 템플릿입니다.

## 1) 폴더 구조

```text
docs/design/
  README.md
  screen-spec-template.md
  qa-checklist-template.md
  v1/
    home.png
    detail.png
    admin-portfolio-form.png
```

## 2) 파일명 규칙

- 화면 시안: `[version]/[screen-name].png`
- 플로우 다이어그램: `[version]/flow-[name].png`
- 메모/수정 이력: `[version]/notes.md`

예시:
- `docs/design/v1/home.png`
- `docs/design/v1/portfolio-detail.png`
- `docs/design/v1/admin-console.png`

## 3) 전달 최소 세트

- 화면 이미지 3장 이상 (홈/상세/관리자)
- `screen-spec-template.md` 복사본 작성
- `qa-checklist-template.md` 복사본 작성

## 4) Figma 링크를 같이 줄 때

- 링크 1개
- 기준 프레임명 목록
- export한 PNG 경로

예시:
- Figma: `https://www.figma.com/file/...`
- 프레임: `Home / Detail / Admin Portfolio Create`
- Export: `docs/design/v2/*.png`

## 5) 전달 시 메세지 예시

```text
시안 v2 반영 요청.
- 링크: (figma url)
- 구현 기준: docs/design/v2/
- 우선순위: 1) 상세 모달 2) 관리자 매핑 폼 3) 홈 필터
```
