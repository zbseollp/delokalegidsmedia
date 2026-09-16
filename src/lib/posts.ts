import { getCollection, type CollectionEntry } from "astro:content";

export type Post = CollectionEntry<"blog">;

/** Payload levert een media-veld als pad of als object; hier wordt het een URL. */
export function imageUrl(value: unknown): string | undefined {
  if (value == null) return undefined;
  if (typeof value === "string") return value.trim() || undefined;
  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    for (const sleutel of ["url", "src", "filename"]) {
      const v = obj[sleutel];
      if (typeof v === "string" && v.trim()) return v.trim();
    }
  }
  return undefined;
}

export function postImage(post: Post): string | undefined {
  const data = post.data as Record<string, unknown>;
  return imageUrl(data.featuredImage) ?? imageUrl(data.heroImage) ?? imageUrl(data.image);
}

/**
 * De URL is de slug uit de frontmatter; laat Payload die weg, dan valt hij
 * terug op de bestandsnaam. Beide worden ontdaan van slashes en extensie,
 * zodat een artikel nooit op /foo.md belandt.
 */
export function postSlug(post: Post): string {
  const uitFrontmatter = typeof post.data.slug === "string" ? post.data.slug.trim() : "";
  const ruw = uitFrontmatter || post.id;
  return ruw.replace(/^\/+|\/+$/g, "").replace(/\.mdx?$/i, "");
}

export function postUrl(post: Post): string {
  return `/${postSlug(post)}/`;
}

function tijd(post: Post): number {
  const d = post.data.pubDate ?? post.data.updatedDate;
  return d instanceof Date ? d.getTime() : 0;
}

/** Gepubliceerde artikelen, nieuwste eerst. */
export async function publishedPosts(): Promise<Post[]> {
  const posts = await getCollection("blog");
  return posts
    .filter((post) => !post.data.draft)
    .filter((post) => {
      const slug = postSlug(post);
      return slug !== "" && !["index", "404", "blog"].includes(slug);
    })
    .sort((a, b) => tijd(b) - tijd(a));
}

export const datumNL = (d: unknown): string =>
  d instanceof Date
    ? new Intl.DateTimeFormat("nl-NL", { day: "numeric", month: "long", year: "numeric" }).format(d)
    : "";
