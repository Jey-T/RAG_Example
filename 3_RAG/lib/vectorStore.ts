import { PGVectorStore } from "@langchain/community/vectorstores/pgvector";
import { Pool } from "pg";
import { LocalE5Embeddings } from "./e5embedding";
import { environmentSchema } from "../schemas/environment";

const safeEnv = environmentSchema.safeParse(process.env);
if (!safeEnv.success) {
    throw new Error("Invalid environment variables");
}

const pool = new Pool({
    host: safeEnv.data.DB_HOST,
    database: safeEnv.data.DB_NAME,
    user: safeEnv.data.DB_USER,
    password: safeEnv.data.DB_PASS,
    port: safeEnv.data.DB_PORT,
    max: 20,
    idleTimeoutMillis: 1000,
    connectionTimeoutMillis: 1000,
    maxUses: 7500,
});

const embeddings = new LocalE5Embeddings({});

export function createVectorStore() {
    return PGVectorStore.initialize(embeddings, {
        pool,
        tableName: "recipes",
        columns: {
            idColumnName: "id",
            vectorColumnName: "embedding",
            contentColumnName: "content",
            metadataColumnName: "metadata",
        }
    });
};
