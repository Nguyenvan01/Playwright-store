import type { DataCase } from './types';

// ---------------------------------------------------------------------------
// Trang chủ - test-data/storefront/home.json
// ---------------------------------------------------------------------------

export interface HomeDeadLinkCase extends DataCase {
  /** Tên link (accessible name) trong <main>. */
  link: string;
  /** Tiêu đề khối chứa link (HOMEWEAR, T-SHIRT...) - để trống = tìm trong khối SẢN PHẨM MỚI / cả trang. */
  section?: string;
  href: string;
}

export interface HomeTabCase extends DataCase {
  tab: string;
  visible: string;
  hidden: string;
}

export interface HomeData {
  /** Response giả cho GET /api/home (đúng shape frontend đọc: { success, data: {...} }). */
  mockHome: { success: boolean; data: Record<string, any> };
  sections: string[];
  banner: { slideHrefs: string[]; overlay: DataCase & { index: number; title: string; expectedHref: string } };
  vouchers: { title: string; description: string; condition: string; validity: string; code: string }[];
  tabs: string[];
  tabCases: HomeTabCase[];
  promoBlocks: { title: string; description: string; cardCount: number }[];
  collections: (DataCase & { titleText: string; ctaText: string; href: string })[];
  clive: string[];
  deadLinks: HomeDeadLinkCase[];
  quickAdd: { product: string; toast: string };
  defaultBannerCount: number;
}

export interface NewsletterCase extends DataCase {
  path: string;
  email: string;
  /** true = hiện "Cảm ơn bạn đã đăng ký!"; false = trình duyệt chặn (validation HTML5). */
  success: boolean;
  /** Thuộc tính ValidityState mong đợi khi bị chặn, vd: "valueMissing", "typeMismatch". */
  validity?: string;
}

export interface FooterLinkCase extends DataCase {
  /** Text của link trong footer; để trống = chỉ cần có link bất kỳ trỏ tới href. */
  link?: string;
  href: string;
}

export interface FooterData {
  headings: string[];
  links: string[];
  linkCases: FooterLinkCase[];
  newsletter: NewsletterCase[];
}

// ---------------------------------------------------------------------------
// Trang danh sách - test-data/storefront/listing.json
// ---------------------------------------------------------------------------

export type ListingKey = 'nam' | 'nu' | 'tre-em' | 'giam-gia';

export interface ListingPageInfo {
  path: string;
  heading: string;
  breadcrumb: string;
  description: string;
  /** server = lọc/sắp xếp qua API (kiểm tra query); client = lọc trên trình duyệt (kiểm tra số lượng). */
  mode: 'server' | 'client';
  /** Mẫu URL (glob) API danh sách sản phẩm của trang - dùng để mock. */
  productsApi: string;
  /** Mẫu URL API danh mục riêng (chỉ trang Trẻ em). */
  categoriesApi?: string;
  sortOptions: string[];
  defaultSort: string;
  sizes: string[];
  colors: string[];
  priceDefault: { from: string; to: string };
  emptyText: string;
  /** Danh mục hiển thị khi dùng dữ liệu mock (5 mục đầu). */
  mockCategories: string[];
}

export interface ListingCase extends DataCase {
  page: ListingKey;
}

export interface ListingSortCase extends ListingCase {
  option: string;
  order: 'asc' | 'desc';
}

/** Kết quả mong đợi khi lọc: query gửi lên API (server) hoặc chữ "Hiển thị n trên t" (client). */
export interface ListingExpect {
  params?: Record<string, string>;
  countText?: string;
}

export interface ListingCategoryCase extends ListingCase, ListingExpect {
  category: string;
}

export interface ListingPriceCase extends ListingCase, ListingExpect {
  from: string;
  to: string;
  min: number;
  max: number;
}

export interface ListingDiscountCase extends ListingCase, ListingExpect {
  label: string;
  minPercent: number;
}

export interface ListingColorCase extends ListingCase, ListingExpect {
  color: string;
}

export interface ListingSizeCase extends ListingCase, ListingExpect {
  size: string;
}

export interface ListingPagingCase extends ListingCase, ListingExpect {
  via: 'number' | 'next' | 'loadMore';
}

export interface ListingData {
  pages: Record<ListingKey, ListingPageInfo>;
  /** Response giả cho API danh sách (dùng chung cho cả 4 trang). */
  mockList: { success: boolean; data: { products: Record<string, unknown>[]; pagination: Record<string, number> } };
  mockEmpty: { success: boolean; data: { products: Record<string, unknown>[]; pagination: Record<string, number> } };
  mockKidsCategories: { success: boolean; data: { id: string; name: string; count: number }[] };
  overlayToast: string;
  showMore: ListingCase & { categories: string[] };
  layout: ListingCase[];
  sort: ListingSortCase[];
  empty: ListingCase[];
  category: ListingCategoryCase[];
  price: ListingPriceCase[];
  discount: ListingDiscountCase[];
  color: ListingColorCase[];
  size: ListingSizeCase[];
  paging: ListingPagingCase[];
  overlayAdd: ListingCase[];
  overlayDetail: ListingCase[];
  favorite: ListingCase[];
}

// ---------------------------------------------------------------------------
// Trang /search - test-data/storefront/search-page.json
// ---------------------------------------------------------------------------

export interface SearchPageCase extends DataCase {
  /** Query string (kèm "?"), vd: "?category=vay". Hỗ trợ ${...}. */
  query: string;
  heading: string;
  breadcrumbs: string[];
  /** Breadcrumb dạng link: [tên, href]. */
  breadcrumbLinks?: [string, string][];
  chips?: { text: string; closeHref: string }[];
}

export interface SearchSortCase extends DataCase {
  query: string;
  option: string;
  order: 'asc' | 'desc';
}

export interface SearchEmptyCase extends DataCase {
  query: string;
  hint: string;
}

export interface SearchPageData {
  sortOptions: string[];
  titles: SearchPageCase[];
  closeChip: DataCase & { query: string; chip: string; heading: string };
  sort: SearchSortCase[];
  empty: SearchEmptyCase[];
  error: DataCase & { message: string };
  paging: (DataCase & { via: 'number' | 'next' })[];
  mockPagination: Record<string, number>;
  shortQuery: DataCase & { keyword: string };
}

// ---------------------------------------------------------------------------
// Chi tiết sản phẩm - test-data/storefront/product.json
// ---------------------------------------------------------------------------

export interface ReviewValidationCase extends DataCase {
  stars: number;
  content: string;
  errors: string[];
}

export interface ReviewServerCase extends DataCase {
  stars: number;
  content: string;
  status: number;
  /** Message backend trả về trong body. */
  message: string;
  /** Toast mong đợi trên UI. */
  toast: string;
}

export interface ProductExtrasData {
  mockSlug: string;
  /** Response giả cho GET /api/products/:slug. */
  mockProduct: { success: boolean; data: Record<string, any> };
  expected: {
    title: string;
    sku: string;
    price: string;
    comparePrice: string;
    discount: string;
    colors: string[];
    imageCount: number;
    description: string[];
    materials: string[];
    care: string[];
    services: { title: string; desc: string }[];
    relatedName: string;
  };
  accordions: string[];
  priceBug: DataCase & { expected: string };
  shippingThresholdBug: DataCase & { service: string; expected: string };
  reviewValidation: ReviewValidationCase[];
  reviewSuccess: DataCase & { stars: number; content: string; message: string };
  reviewServerErrors: ReviewServerCase[];
}

// ---------------------------------------------------------------------------
// Blog - test-data/storefront/blog.json
// ---------------------------------------------------------------------------

export interface BlogArticle {
  id: number;
  title: string;
  slug: string;
  summary?: string;
  category?: string;
  tags?: string | string[] | null;
  view_count?: number;
  author_name?: string;
  published_at?: string;
  content?: string | null;
  thumbnail?: string;
}

export interface BlogFilterCase extends DataCase {
  category: string;
  titles: string[];
}

/** Kết quả mong đợi trên trang chi tiết bài viết. */
export interface BlogArticleExpect {
  slug: string;
  titleText: string;
  category: string;
  views: string;
  author: string;
  /** Tag của bài viết (hiển thị "#tag"). */
  articleTags: string[];
  related: string[];
  fallback?: boolean;
}

export interface BlogDetailCase extends DataCase, BlogArticleExpect {}

export interface BlogData {
  mockList: { success: boolean; news: BlogArticle[] };
  pills: string[];
  filters: BlogFilterCase[];
  details: BlogDetailCase[];
  invalidSlug: string;
  newsletterBug: DataCase & { email: string };
}

// ---------------------------------------------------------------------------
// Trang tĩnh - test-data/storefront/static-pages.json
// ---------------------------------------------------------------------------

export interface StaticPageCase extends DataCase {
  path: string;
  h1: string;
  h2: string[];
  h3: string[];
  texts: string[];
}

export interface ContentBugCase extends DataCase {
  path: string;
  /** Tiêu đề h3 của khối cần kiểm tra (để trống = cả <main>). */
  block?: string;
  /** Chuỗi phải xuất hiện (nếu có). */
  mustContain?: string;
  /** Biểu thức chính quy KHÔNG được xuất hiện trong <main> (nếu có). */
  mustNotMatch?: string;
}

export interface UnknownRouteCase extends DataCase {
  path: string;
  message: string;
}

export interface StaticPagesData {
  pages: StaticPageCase[];
  contentBugs: ContentBugCase[];
  unknownRoutes: UnknownRouteCase[];
}
