import ast
from typing import List, Dict, Any, Tuple, Callable
import logging

def _parse_field(field_str: str, prefixes_handlers: List[Tuple[str, Callable[[str], List[str]]]]) -> list[str]:
    """
    Generic parser for CSV fields that can be either R c() vectors or single strings.
    
    Args:
        field_str: The string to parse
        prefixes_handlers: A list of tuples, each containing a prefix and a handler function
    """

    for prefix, handler in prefixes_handlers:
        if field_str.startswith(prefix):
            return handler(field_str)
        
    return []

def parse_c_list(s: str, logger: logging.Logger) -> list[str]:
    try:
        inside = s.strip()[2:-1]
        return ast.literal_eval("[" + inside + "]")
    except Exception as e:
        logger.error(f"Error parsing c list for {s}: {e}")
        raise e

def _parse_ol(list: List[str], logger: logging.Logger) -> str:
    try:
        result = ""
        for index, step in enumerate(list):
                result += f"{index + 1}) " + step + "\n"
        return result
    except Exception as e:
        logger.error(f"Error parsing ol for {list}: {e}")
        raise e

def _parse_ul(list: List[str], logger: logging.Logger) -> str:
    try:
        result = ""
        for step in list:
            result += "- " + step + "\n"
        return result
    except Exception as e:
        logger.error(f"Error parsing ul for {list}: {e}")
        raise e

def parse_images(str: str, logger: logging.Logger) -> list[str]:
    try:
        return _parse_field(str, [("c(", lambda x: parse_c_list(x, logger)), ("\"http", lambda x: [x])])
    except Exception as e:
        logger.error(f"Error parsing images for {str}: {e}")
        raise e

def parse_instructions(str: str, logger: logging.Logger) -> list[str]:
    try:
        return _parse_field(str, [("c(", lambda x: parse_c_list(x, logger)), ("\"", lambda x: [x])])
    except Exception as e:
        logger.error(f"Error parsing instructions for {str}: {e}")
        raise e

def _parse_keywords(str: str, logger: logging.Logger) -> list[str]:
    try:
        return _parse_field(str, [("c(", lambda x: parse_c_list(x, logger))])
    except Exception as e:
        logger.error(f"Error parsing keywords for {str}: {e}")
        raise e

def _parse_ingredients(str: str, logger: logging.Logger) -> list[str]:
    try:
        return _parse_field(str, [("c(", lambda x: parse_c_list(x, logger))])
    except Exception as e:
        logger.error(f"Error parsing ingredients for {str}: {e}")
        raise e

def parse_metadata(recipe: Dict[str, str], logger: logging.Logger) -> Dict[str, Any]:
    try:
        ingredients = _parse_ingredients(recipe["RecipeIngredientParts"], logger)
        keywords = _parse_keywords(recipe["Keywords"], logger)
        images = parse_images(recipe["Images"], logger)
        instructions = parse_instructions(recipe["RecipeInstructions"], logger)
        calories = float(recipe["Calories"])
        fat = float(recipe["FatContent"])
        saturated_fat = float(recipe["SaturatedFatContent"])
        cholesterol = float(recipe["CholesterolContent"])
        sodium = float(recipe["SodiumContent"])
        carbohydrates = float(recipe["CarbohydrateContent"])
        fiber = float(recipe["FiberContent"])
        sugar = float(recipe["SugarContent"])
        protein = float(recipe["ProteinContent"])

        return {
            "data": {"name": recipe["Name"], "category": recipe["RecipeCategory"],
            "keywords": keywords,
            "ingredients": ingredients,
            "description": recipe["Description"],
            "cook_time": recipe["CookTime"],
            "prep_time": recipe["PrepTime"],
            "total_time": recipe["TotalTime"],
            "n_ingredients": len(ingredients),
            "n_steps": len(instructions),
            'images': images,
            'instructions': instructions,
            'calories': calories,
            'fat': fat,
            'saturated_fat': saturated_fat,
            'cholesterol': cholesterol,
            'sodium': sodium,
            'carbohydrates': carbohydrates,
            'fiber': fiber,
            'sugar': sugar,
            'protein': protein},
            "success": True
                }
    
    except Exception as e:
        logger.error(f"Error parsing metadata for {recipe['Name']}: {e}")
        return {}

def parse_content(recipe: Dict[str, str], logger: logging.Logger) -> Dict[str, Any]:
    try:
        ingredients = _parse_ingredients(recipe["RecipeIngredientParts"], logger)
        keywords = _parse_keywords(recipe["Keywords"], logger)
        instructions = parse_instructions(recipe["RecipeInstructions"], logger)
        return {"data":f"""name: {recipe["Name"]}
    category: {recipe["RecipeCategory"]}
    {len(instructions)} steps, {len(ingredients)} ingredients
    preparation time: {recipe["PrepTime"]}
    cooking time: {recipe["CookTime"]}
    total time: {recipe["TotalTime"]}
    keywords: {", ".join(keywords,)}

    calories: {recipe["Calories"]} kcal
    fat: {recipe["FatContent"]} g
    saturated_fat: {recipe["SaturatedFatContent"]} g
    cholesterol: {recipe["CholesterolContent"]} mg
    carbohydrates: {recipe["CarbohydrateContent"]} g
    sugar: {recipe["SugarContent"]} g
    sodium: {recipe["SodiumContent"]} mg
    fiber: {recipe["FiberContent"]} g
    protein: {recipe["ProteinContent"]} g

    ingredients:
    {_parse_ul(ingredients, logger)}

    instructions:
    {_parse_ol(instructions, logger)}

    description:
    {recipe["Description"]}""", "success": True}
    except Exception as e:
        logger.error(f"Error parsing content for {recipe['Name']}: {e}")
        return {"data": None, "success": False}