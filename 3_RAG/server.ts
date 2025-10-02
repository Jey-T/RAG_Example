import "dotenv/config";
import express from "express";
import { createServer } from "http";
import { environmentSchema } from "./schemas/environment";
import { errorHandler } from "./middlewares/errorHandler";
import limiter from "./middlewares/rateLimitHandler";
import healthCheck from "./handlers/health";
import notFound from "./handlers/not-found";
import gracefulShutdown from "./handlers/shutdown";
import { createVectorStore } from "./lib/vectorStore";
import embed from "./handlers/embed";

async function main() {
    
    const parsedEnv = environmentSchema.safeParse(process.env);
    if (!parsedEnv.success) {
        console.error("Invalid environment variables");
        process.exit(1);
    }

    const vectorStore = await createVectorStore();
    
    const app = express();
    const server = createServer(app);

    app.use(limiter);
    app.use(express.json());
    app.use(errorHandler);

    app.post("/embedding", async (req, res, next) => embed(req, res, next, vectorStore));
    app.get("/health", healthCheck);
    app.all("/{*any}", notFound);

    server.listen(parsedEnv.data.PORT, () => {
        console.log("Embedding service is running on port 4000");
    });

    process.on('SIGTERM', () => gracefulShutdown(server, vectorStore, 'SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown(server, vectorStore, 'SIGINT'));
}

main();