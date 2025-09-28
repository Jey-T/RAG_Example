import { z } from "zod/v4";

const embeddingRequestSchema = z.object({
    question: z.string().startsWith("query: ", { message: "query input must start with 'query: '" })
});

export { embeddingRequestSchema };