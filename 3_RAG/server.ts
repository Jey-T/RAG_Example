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
import retrieve from "./handlers/retrieve";
import cors from "cors";

async function main() {

    const parsedEnv = environmentSchema.safeParse(process.env);
    if (!parsedEnv.success) {
        console.error("Invalid environment variables");
        process.exit(1);
    }

    const vectorStore = await createVectorStore();

    const PORT = parsedEnv.data.PORT;
    const app = express();
    const server = createServer(app);
    
    app.set('trust proxy', true);
    app.use(cors());
    app.use(express.json());
    app.use(limiter);
    app.use(errorHandler);

    app.post("/retrieve", async (req, res, next) => retrieve(req, res, next, vectorStore));
    app.get("/health", healthCheck);
    app.all("/{*any}", notFound);

    server.listen(PORT, () => {
        console.log("Embedding service is running on port " + PORT);
    });

    process.on('SIGTERM', () => gracefulShutdown(server, vectorStore, 'SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown(server, vectorStore, 'SIGINT'));
}

main();