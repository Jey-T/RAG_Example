interface Recipe {
    id: number;
    name: string;
    steps: number;
    ingredients: number;
    image: string;
    link: string;
}

export interface ApiResult {
    answer: string;
    recipes: Recipe[];
}