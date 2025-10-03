import { z } from "zod/v4";

const graphResultSchema = z.object({
    answer: z.string(),
    context: z.array(z.object({
        metadata: z.object({
            name: z.string(),
            n_steps: z.number(),
            n_ingredients: z.number(),
            images: z.string().array(),
            recipe_id: z.coerce.number(),
        }),
    })),
});

export { graphResultSchema };