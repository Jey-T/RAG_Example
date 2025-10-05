import { graphResultSchema } from "../schemas/graphResult";
import { ValidationError } from "../types/error";
import { ApiResult } from "../types/apiResult";

export type GraphResult = {
    question: string;
    context: { id?: string; metadata: Record<string, any> }[];
    answer: string;
}

export function processResult(result: GraphResult): ApiResult {

    const parsedResult = graphResultSchema.safeParse(result);
    if (!parsedResult.success) {
        throw new ValidationError(parsedResult.error.message);
    }

    const { answer, context } = parsedResult.data;

    return {
        answer,
        recipes: context.map((recipe) => {
            const image = recipe.metadata.images?.[0] ?? "";
            const link = `https://www.food.com/recipe/${recipe.metadata.name.toLowerCase().replace(/ /g, "-")}-${recipe.metadata.recipe_id}`;
            return ({
                id: recipe.metadata.recipe_id,
                name: recipe.metadata.name,
                steps: recipe.metadata.n_steps,
                ingredients: recipe.metadata.n_ingredients,
                image,
                link,
            })
        }),
    }
}