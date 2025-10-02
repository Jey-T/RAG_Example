import { z } from "zod/v4";

const embeddingRequestSchema = z.object({
    question: z.string()
    .startsWith("query: ", { message: "query input must start with 'query: '" })
    .max(100, { message: "query input must be less than 100 characters" })
});

export { embeddingRequestSchema };