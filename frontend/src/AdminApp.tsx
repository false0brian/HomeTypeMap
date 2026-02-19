import { FormEvent, MouseEvent, useEffect, useMemo, useState } from "react";

import {
  adminCreateBlogPost,
  adminCreatePortfolio,
  adminListBlogPosts,
  adminListPortfolios,
  adminUpdateBlogStatus,
  adminUpdatePortfolioStatus,
} from "./api";
import type { AdminBlogPost, AdminPortfolio, PublishStatus } from "./types";

const DEFAULT_ADMIN_KEY = import.meta.env.VITE_ADMIN_API_KEY ?? "";

const SAMPLE_BEFORE_1 = "/samples/portfolio-before-1.svg";
const SAMPLE_AFTER_1 = "/samples/portfolio-after-1.svg";
const SAMPLE_BEFORE_2 = "/samples/portfolio-before-2.svg";
const SAMPLE_AFTER_2 = "/samples/portfolio-after-2.svg";
const SAMPLE_FLOORPLAN = "/samples/floorplan-59a.svg";

type PinTarget = { rowIndex: number; kind: "before" | "after" };

type ImagePairForm = {
  sort_order: string;
  before_url: string;
  after_url: string;
  before_area_label: string;
  after_area_label: string;
  before_x: string;
  before_y: string;
  after_x: string;
  after_y: string;
};

function safeNum(v: string): number | undefined {
  const t = v.trim();
  if (!t) return undefined;
  const n = Number(t);
  return Number.isFinite(n) ? n : undefined;
}

function makePair(order: number): ImagePairForm {
  return {
    sort_order: String(order),
    before_url: "",
    after_url: "",
    before_area_label: "",
    after_area_label: "",
    before_x: "",
    before_y: "",
    after_x: "",
    after_y: "",
  };
}

export default function AdminApp() {
  const [adminKey, setAdminKey] = useState(DEFAULT_ADMIN_KEY);
  const [status, setStatus] = useState("관리자 콘솔 준비 중");
  const [portfolios, setPortfolios] = useState<AdminPortfolio[]>([]);
  const [posts, setPosts] = useState<AdminBlogPost[]>([]);
  const [pinTarget, setPinTarget] = useState<PinTarget>({ rowIndex: 0, kind: "before" });
  const [imagePairs, setImagePairs] = useState<ImagePairForm[]>([makePair(1)]);
  const [portfolioForm, setPortfolioForm] = useState({
    complex_id: "101",
    unit_type_id: "1001",
    vendor_id: "501",
    title: "",
    unit_floorplan_url: "",
    work_scope: "partial",
    style: "minimal",
    summary: "",
    tags: "",
    budget_min_krw: "",
    budget_max_krw: "",
    duration_days: "",
    status: "draft" as PublishStatus,
  });
  const [blogForm, setBlogForm] = useState({
    vendor_id: "501",
    title: "",
    slug: "",
    excerpt: "",
    content: "",
    status: "draft" as PublishStatus,
  });

  async function refreshAll() {
    if (!adminKey.trim()) {
      setStatus("X-Admin-Key를 입력하세요.");
      return;
    }
    try {
      const [nextPortfolios, nextPosts] = await Promise.all([
        adminListPortfolios(adminKey.trim()),
        adminListBlogPosts(adminKey.trim()),
      ]);
      setPortfolios(nextPortfolios);
      setPosts(nextPosts);
      setStatus(`불러오기 완료: 포트폴리오 ${nextPortfolios.length}개, 블로그 ${nextPosts.length}개`);
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "관리자 데이터를 불러오지 못했습니다.");
    }
  }

  useEffect(() => {
    if (!adminKey.trim()) return;
    void refreshAll();
  }, []);

  const floorplanPreview = useMemo(
    () => portfolioForm.unit_floorplan_url.trim() || SAMPLE_FLOORPLAN,
    [portfolioForm.unit_floorplan_url],
  );

  function updatePair(index: number, patch: Partial<ImagePairForm>) {
    setImagePairs((prev) => prev.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  }

  function addPairRow() {
    setImagePairs((prev) => [...prev, makePair(prev.length + 1)]);
  }

  function removePairRow(index: number) {
    setImagePairs((prev) => {
      if (prev.length === 1) return prev;
      return prev.filter((_, i) => i !== index).map((row, i) => ({ ...row, sort_order: String(i + 1) }));
    });
  }

  function onPickFloorplanPosition(e: MouseEvent<HTMLDivElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round(((e.clientX - rect.left) / rect.width) * 100);
    const y = Math.round(((e.clientY - rect.top) / rect.height) * 100);
    const safeX = String(Math.max(0, Math.min(100, x)));
    const safeY = String(Math.max(0, Math.min(100, y)));

    updatePair(
      pinTarget.rowIndex,
      pinTarget.kind === "before" ? { before_x: safeX, before_y: safeY } : { after_x: safeX, after_y: safeY },
    );
  }

  async function onCreatePortfolio(e: FormEvent) {
    e.preventDefault();
    try {
      const beforeItems = imagePairs
        .filter((row) => row.before_url.trim())
        .map((row) => ({
          image_url: row.before_url.trim(),
          sort_order: safeNum(row.sort_order),
          area_label: row.before_area_label.trim() || undefined,
          floorplan_x: safeNum(row.before_x),
          floorplan_y: safeNum(row.before_y),
        }));

      const afterItems = imagePairs
        .filter((row) => row.after_url.trim())
        .map((row) => ({
          image_url: row.after_url.trim(),
          sort_order: safeNum(row.sort_order),
          area_label: row.after_area_label.trim() || undefined,
          floorplan_x: safeNum(row.after_x),
          floorplan_y: safeNum(row.after_y),
        }));

      await adminCreatePortfolio(adminKey.trim(), {
        complex_id: Number(portfolioForm.complex_id),
        unit_type_id: Number(portfolioForm.unit_type_id),
        vendor_id: Number(portfolioForm.vendor_id),
        title: portfolioForm.title,
        unit_floorplan_url: portfolioForm.unit_floorplan_url.trim() || undefined,
        work_scope: portfolioForm.work_scope,
        style: portfolioForm.style,
        summary: portfolioForm.summary.trim() || undefined,
        tags: portfolioForm.tags.trim() || undefined,
        budget_min_krw: safeNum(portfolioForm.budget_min_krw),
        budget_max_krw: safeNum(portfolioForm.budget_max_krw),
        duration_days: safeNum(portfolioForm.duration_days),
        before_image_items: beforeItems,
        after_image_items: afterItems,
        status: portfolioForm.status,
      });

      setPortfolioForm((prev) => ({
        ...prev,
        title: "",
        summary: "",
        tags: "",
        budget_min_krw: "",
        budget_max_krw: "",
        duration_days: "",
      }));
      await refreshAll();
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "포트폴리오 등록 실패");
    }
  }

  async function onCreateBlogPost(e: FormEvent) {
    e.preventDefault();
    try {
      await adminCreateBlogPost(adminKey.trim(), {
        vendor_id: Number(blogForm.vendor_id),
        title: blogForm.title,
        slug: blogForm.slug,
        excerpt: blogForm.excerpt,
        content: blogForm.content,
        status: blogForm.status,
      });
      setBlogForm((prev) => ({ ...prev, title: "", slug: "", excerpt: "", content: "" }));
      await refreshAll();
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "블로그 등록 실패");
    }
  }

  async function publishPortfolio(portfolioId: number) {
    try {
      await adminUpdatePortfolioStatus(adminKey.trim(), portfolioId, "published");
      await refreshAll();
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "포트폴리오 상태 변경 실패");
    }
  }

  async function publishBlogPost(postId: number) {
    try {
      await adminUpdateBlogStatus(adminKey.trim(), postId, "published");
      await refreshAll();
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "블로그 상태 변경 실패");
    }
  }

  function fillSampleImages() {
    setPortfolioForm((prev) => ({
      ...prev,
      unit_floorplan_url: SAMPLE_FLOORPLAN,
    }));
    setImagePairs([
      {
        sort_order: "1",
        before_url: SAMPLE_BEFORE_1,
        after_url: SAMPLE_AFTER_1,
        before_area_label: "거실",
        after_area_label: "거실",
        before_x: "35",
        before_y: "62",
        after_x: "35",
        after_y: "62",
      },
      {
        sort_order: "2",
        before_url: SAMPLE_BEFORE_2,
        after_url: SAMPLE_AFTER_2,
        before_area_label: "주방",
        after_area_label: "주방",
        before_x: "68",
        before_y: "46",
        after_x: "68",
        after_y: "46",
      },
    ]);
    setPinTarget({ rowIndex: 0, kind: "before" });
  }

  return (
    <div className="admin-page">
      <header className="admin-header">
        <div>
          <h1>Partner Console</h1>
          <p>업체 관리자용 포트폴리오/블로그 CMS</p>
        </div>
        <div className="admin-key-box">
          <label>X-Admin-Key</label>
          <input value={adminKey} onChange={(e) => setAdminKey(e.target.value)} placeholder="dev-admin-key" />
          <button onClick={() => void refreshAll()}>새로고침</button>
        </div>
      </header>

      <p className="admin-status">{status}</p>

      <main className="admin-grid">
        <section className="admin-panel">
          <h2>포트폴리오 등록</h2>
          <form className="admin-form" onSubmit={onCreatePortfolio}>
            <input value={portfolioForm.complex_id} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, complex_id: e.target.value }))} placeholder="complex_id" />
            <input value={portfolioForm.unit_type_id} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, unit_type_id: e.target.value }))} placeholder="unit_type_id" />
            <input value={portfolioForm.vendor_id} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, vendor_id: e.target.value }))} placeholder="vendor_id" />
            <input value={portfolioForm.title} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, title: e.target.value }))} placeholder="포트폴리오 제목" required />
            <input value={portfolioForm.unit_floorplan_url} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, unit_floorplan_url: e.target.value }))} placeholder="unit_floorplan_url" />

            <div className="admin-inline">
              <button type="button" className="ghost-btn" onClick={fillSampleImages}>다중 샘플 매핑 채우기</button>
              <button type="button" className="ghost-btn" onClick={addPairRow}>매핑 행 추가</button>
            </div>

            {imagePairs.map((row, i) => (
              <div key={i} className="pair-row">
                <div className="pair-head">
                  <strong>매핑 #{i + 1}</strong>
                  <button type="button" className="ghost-btn" onClick={() => removePairRow(i)}>삭제</button>
                </div>
                <div className="admin-inline">
                  <input value={row.sort_order} onChange={(e) => updatePair(i, { sort_order: e.target.value })} placeholder="sort_order" />
                  <input value={row.before_url} onChange={(e) => updatePair(i, { before_url: e.target.value })} placeholder="before_image_url" />
                  <input value={row.after_url} onChange={(e) => updatePair(i, { after_url: e.target.value })} placeholder="after_image_url" />
                </div>
                <div className="admin-inline">
                  <input value={row.before_area_label} onChange={(e) => updatePair(i, { before_area_label: e.target.value })} placeholder="before_area_label" />
                  <input value={row.after_area_label} onChange={(e) => updatePair(i, { after_area_label: e.target.value })} placeholder="after_area_label" />
                </div>
                <div className="admin-inline">
                  <input value={row.before_x} onChange={(e) => updatePair(i, { before_x: e.target.value })} placeholder="before_x" />
                  <input value={row.before_y} onChange={(e) => updatePair(i, { before_y: e.target.value })} placeholder="before_y" />
                  <input value={row.after_x} onChange={(e) => updatePair(i, { after_x: e.target.value })} placeholder="after_x" />
                  <input value={row.after_y} onChange={(e) => updatePair(i, { after_y: e.target.value })} placeholder="after_y" />
                </div>
                <div className="admin-inline">
                  <button type="button" className={pinTarget.rowIndex === i && pinTarget.kind === "before" ? "pin-tab active" : "pin-tab"} onClick={() => setPinTarget({ rowIndex: i, kind: "before" })}>#{i + 1} Before 핀</button>
                  <button type="button" className={pinTarget.rowIndex === i && pinTarget.kind === "after" ? "pin-tab active" : "pin-tab"} onClick={() => setPinTarget({ rowIndex: i, kind: "after" })}>#{i + 1} After 핀</button>
                </div>
              </div>
            ))}

            <div className="admin-pin-toolbar">
              <span>활성 대상: #{pinTarget.rowIndex + 1} {pinTarget.kind.toUpperCase()} · 평면도 클릭으로 핀 좌표 입력</span>
            </div>

            <div className="admin-floorplan-picker" onClick={onPickFloorplanPosition}>
              <img src={floorplanPreview} alt="floorplan picker" />
              {imagePairs.map((row, i) => (
                <div key={`pin-${i}`}>
                  {row.before_x && row.before_y ? <span className="picker-pin before" style={{ left: `${row.before_x}%`, top: `${row.before_y}%` }}>B{i + 1}</span> : null}
                  {row.after_x && row.after_y ? <span className="picker-pin after" style={{ left: `${row.after_x}%`, top: `${row.after_y}%` }}>A{i + 1}</span> : null}
                </div>
              ))}
            </div>

            <input value={portfolioForm.work_scope} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, work_scope: e.target.value }))} placeholder="work_scope" required />
            <input value={portfolioForm.style} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, style: e.target.value }))} placeholder="style" required />
            <textarea value={portfolioForm.summary} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, summary: e.target.value }))} placeholder="요약 설명" rows={3} />
            <input value={portfolioForm.tags} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, tags: e.target.value }))} placeholder="태그" />
            <div className="admin-inline">
              <input type="number" value={portfolioForm.budget_min_krw} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, budget_min_krw: e.target.value }))} placeholder="budget_min_krw" />
              <input type="number" value={portfolioForm.budget_max_krw} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, budget_max_krw: e.target.value }))} placeholder="budget_max_krw" />
              <input type="number" value={portfolioForm.duration_days} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, duration_days: e.target.value }))} placeholder="duration_days" />
            </div>
            <select value={portfolioForm.status} onChange={(e) => setPortfolioForm((prev) => ({ ...prev, status: e.target.value as PublishStatus }))}>
              <option value="draft">draft</option>
              <option value="review">review</option>
              <option value="published">published</option>
            </select>
            <button type="submit">포트폴리오 저장</button>
          </form>

          <div className="admin-list">
            {portfolios.map((item) => (
              <article key={item.portfolio_id} className="admin-card">
                <h3>{item.title}</h3>
                <p>
                  #{item.portfolio_id} / status: <strong>{item.status}</strong>
                </p>
                {item.summary ? <p className="admin-card-summary">{item.summary}</p> : null}
                <div className="admin-thumb-row">
                  <img src={item.before_image_url || SAMPLE_BEFORE_1} alt="before" />
                  <img src={item.after_image_url || SAMPLE_AFTER_1} alt="after" />
                </div>
                <button onClick={() => void publishPortfolio(item.portfolio_id)}>발행 처리</button>
              </article>
            ))}
          </div>
        </section>

        <section className="admin-panel">
          <h2>블로그 등록</h2>
          <form className="admin-form" onSubmit={onCreateBlogPost}>
            <input value={blogForm.vendor_id} onChange={(e) => setBlogForm((prev) => ({ ...prev, vendor_id: e.target.value }))} placeholder="vendor_id" />
            <input value={blogForm.title} onChange={(e) => setBlogForm((prev) => ({ ...prev, title: e.target.value }))} placeholder="제목" required />
            <input value={blogForm.slug} onChange={(e) => setBlogForm((prev) => ({ ...prev, slug: e.target.value }))} placeholder="slug" required />
            <input value={blogForm.excerpt} onChange={(e) => setBlogForm((prev) => ({ ...prev, excerpt: e.target.value }))} placeholder="요약" />
            <textarea value={blogForm.content} onChange={(e) => setBlogForm((prev) => ({ ...prev, content: e.target.value }))} placeholder="본문" rows={5} required />
            <select value={blogForm.status} onChange={(e) => setBlogForm((prev) => ({ ...prev, status: e.target.value as PublishStatus }))}>
              <option value="draft">draft</option>
              <option value="review">review</option>
              <option value="published">published</option>
            </select>
            <button type="submit">블로그 저장</button>
          </form>

          <div className="admin-list">
            {posts.map((post) => (
              <article key={post.post_id} className="admin-card">
                <h3>{post.title}</h3>
                <p>
                  @{post.slug} / status: <strong>{post.status}</strong>
                </p>
                <button onClick={() => void publishBlogPost(post.post_id)}>발행 처리</button>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
