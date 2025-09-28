import { NextFunction, Request, Response } from "express";
import createGraph from "../lib/langchain";
import { VectorStore } from "@langchain/core/vectorstores";
import { EmbeddingError, ValidationError } from "../types/error";
import { embeddingRequestSchema } from "../schemas/embeddingInput";

export default async function embed(req: Request, res: Response, next: NextFunction, vectorStore: VectorStore) {
    try {
        const parsedInput = embeddingRequestSchema.safeParse(req.body);
        if (!parsedInput.success) {
            next(new ValidationError(parsedInput.error.message));
            return;
        }
        const question = parsedInput.data.question;
        const graph = await createGraph(vectorStore);
        const result = await graph.invoke({ question });
        return res.status(200).json({ data: result, status: "ok", timestamp: new Date().toISOString() });
    } catch (error) {
        console.log(error);
        next(new EmbeddingError());
    }

}