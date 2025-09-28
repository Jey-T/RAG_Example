import { z } from "zod/v4";

const environmentSchema = z.object({
    PORT: z.string().default("4000"),
    DB_HOST: z.string().default("localhost"),
    DB_PORT: z.string().default("5432"),
    DB_USER: z.string().default("postgres"),
    DB_PASS: z.string().default("postgres"),
    DB_NAME: z.string().default("postgres"),
});

export { environmentSchema };