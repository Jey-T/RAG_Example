
import { Document } from "@langchain/core/documents";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { Annotation, StateGraph } from "@langchain/langgraph";
import { llm } from "./llm";
import { VectorStore } from "@langchain/core/vectorstores";

export default async function createGraph(vectorStore: VectorStore) {

    // Define prompt for question-answering
    const promptTemplate = ChatPromptTemplate.fromTemplate(`
        You are a helpful cooking assistant. Based on the provided recipe context, give the user a list of recipes.
        
        When providing recipes, always include the recipes names, number of steps and number of ingredients. Always give all 5 recipes even if they are not relevant to the question, though you should warn the user that some of the recipes are not relevant.
        
        Context (recipes):
        {context}
        
        Question: {question}
        
        Please provide a short list of recipes names in the response:`);

    // Define state for application
    const InputStateAnnotation = Annotation.Root({
        question: Annotation<string>,
    });

    const StateAnnotation = Annotation.Root({
        question: Annotation<string>,
        context: Annotation<Document[]>,
        answer: Annotation<string>,
    });

    // Define application steps
    const retrieve = async (state: typeof InputStateAnnotation.State) => {
        const retrievedDocs = await vectorStore.similaritySearch(state.question, 5)
        return { context: retrievedDocs };
    };


    const generate = async (state: typeof StateAnnotation.State) => {
        const docsContent = state.context.map(doc => doc.pageContent).join("\n");
        const messages = await promptTemplate.invoke({ question: state.question, context: docsContent });
        const response = await llm.invoke(messages);
        return { answer: response.content };
    };


    // Compile application and test
    const graph = new StateGraph(StateAnnotation)
        .addNode("retrieve", retrieve)
        .addNode("generate", generate)
        .addEdge("__start__", "retrieve")
        .addEdge("retrieve", "generate")
        .addEdge("generate", "__end__")
        .compile();

    return graph;
}
