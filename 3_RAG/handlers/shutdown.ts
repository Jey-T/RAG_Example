
import { PGVectorStore } from "@langchain/community/vectorstores/pgvector";
import { Server } from "http";

export default async function gracefulShutdown(server: Server, vectorStore: PGVectorStore, signal: string) {
    console.log(`Received ${signal}. Shutting down mailing service gracefully...`);
    console.log("Closing database connections...")
    await vectorStore.client.release()
    server.close((err) => {
        if (err) {
            console.error('Error during shutdown:', err);
            process.exit(1);
        }

        console.log('Embedding service stopped successfully');
        process.exit(0);
    });

    setTimeout(() => {
        console.error('Force shutdown after timeout');
        process.exit(1);
    }, 15000);
}