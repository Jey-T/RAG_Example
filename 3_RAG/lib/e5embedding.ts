import { Embeddings } from "@langchain/core/embeddings";

export class LocalE5Embeddings extends Embeddings {
  async embedQuery(text: string): Promise<number[]> {
    try {
      const res = await fetch(`${process.env.EMBEDDING_SERVICE_URL}/embedding`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        throw new Error(`Embedding service error: ${res.status}`);
      }

      const data = await res.json();
      return data.embedding;
    } catch (error) {
      throw new Error(`Failed to get embedding: ${error.message}`);
    }

  }

  async embedDocuments(documents: string[]): Promise<number[][]> {
    throw new Error("embedDocuments is not supported by LocalE5Embeddings because it is not needed for this application");
  }
}
