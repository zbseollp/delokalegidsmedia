import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

/**
 * De artikelen komen uit Payload en worden bij elke deploy naar
 * src/content/blog geschreven. Payload laat velden weg, zet ze op null of
 * levert een media-object in plaats van een pad; het schema hieronder
 * accepteert al die vormen. Zonder die tolerantie valt een heel artikel uit de
 * collectie en verdwijnt het van de site.
 */
const mediaValue = z
  .union([
    z.string(),
    z
      .object({
        url: z.string().optional(),
        src: z.string().optional(),
        filename: z.string().optional(),
        alt: z.string().optional(),
      })
      .passthrough(),
  ])
  .nullish();

const optionalText = z.preprocess(
  (val) => (val == null || val === "" ? undefined : String(val)),
  z.string().optional(),
);

const optionalDate = z.preprocess((val) => {
  if (val == null || val === "") return undefined;
  const parsed = val instanceof Date ? val : new Date(val as string | number);
  return Number.isNaN(parsed.getTime()) ? undefined : parsed;
}, z.date().optional());

/** Categorieën en tags komen soms als losse string of als getal binnen. */
const stringList = z.preprocess((val) => {
  if (Array.isArray(val)) return val.map((item) => String(item).trim()).filter(Boolean);
  if (typeof val === "string" && val.trim()) return [val.trim()];
  return [];
}, z.array(z.string()));

/** Payload zet `draft` als boolean of als de tekst "true". */
function isDraft(val: unknown): boolean {
  if (typeof val === "boolean") return val;
  if (typeof val === "string") return val.trim().toLowerCase() === "true";
  return false;
}

const blog = defineCollection({
  loader: glob({ base: "./src/content/blog", pattern: "**/*.{md,mdx}" }),
  schema: z
    .object({
      title: z.preprocess((val) => (val == null ? "" : String(val)), z.string()),
      description: optionalText,
      excerpt: optionalText,
      metaDescription: optionalText,
      pubDate: optionalDate,
      date: optionalDate,
      updatedDate: optionalDate,
      slug: optionalText,
      author: optionalText,
      heroImage: mediaValue,
      featuredImage: mediaValue,
      image: mediaValue,
      featuredImageAlt: optionalText,
      categories: stringList,
      tags: stringList,
      draft: z.unknown().optional(),
      _status: optionalText,
      publishStatus: optionalText,
    })
    .passthrough()
    .transform((data) => ({
      ...data,
      description: data.description ?? data.excerpt ?? data.metaDescription,
      pubDate: data.pubDate ?? data.date,
      draft: isDraft(data.draft) || data._status === "draft" || data.publishStatus === "draft",
    })),
});

export const collections = { blog };
