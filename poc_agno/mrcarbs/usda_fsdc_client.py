import os

from dotenv import load_dotenv
from usda_fdc import FdcClient


class FoodCarbFinder:
    EXCLUDE_KEYWORDS = ["pie", "juice", "cider", "sauce", "jam", "preserve", "dried", "chips"]

    def __init__(self, api_key: str):
        self.client = FdcClient(api_key)

    def get_carbs(self, food_name: str, exact: bool = False):
        results = self.client.search(food_name)
        if not results.foods:
            return None, None

        # If exact match requested, check for exact description
        if exact:
            for food in results.foods:
                if food.description.lower() == food_name.lower():
                    return food.description, self._extract_carbs(food.fdc_id)

        # Otherwise, pick the best filtered match
        for food in results.foods:
            if not self._should_exclude(food.description):
                return food.description, self._extract_carbs(food.fdc_id)

        # Fallback: just return the first
        best_food = results.foods[0]
        return best_food.description, self._extract_carbs(best_food.fdc_id)

    def _extract_carbs(self, fdc_id: int):
        details = self.client.get_food(fdc_id)

        # --- Carbs per 100 g (nutrient id 1005) ---
        carbs_per_100g = None
        for nutrient in details.nutrients:
            if nutrient.id == 1005:  # Carbohydrate, by difference
                carbs_per_100g = nutrient.amount
                break

        # --- Carbs per serving size (portion) ---
        servings = []
        if hasattr(details, "food_portions"):
            for portion in details.food_portions:
                if not portion.gram_weight:
                    continue

                # scale carbs by portion weight
                if carbs_per_100g is not None:
                    carbs_for_serving = (carbs_per_100g / 100.0) * portion.gram_weight
                    servings.append({
                        "measure": portion.modifier or portion.measure_unit.name,
                        "gram_weight": portion.gram_weight,
                        "carbs": round(carbs_for_serving, 2)
                    })

        return {
            "per_100g": carbs_per_100g,
            "per_serving": servings
        }

    def _should_exclude(self, description: str) -> bool:
        desc_lower = description.lower()
        return any(word in desc_lower for word in self.EXCLUDE_KEYWORDS)


if __name__ == "__main__":
    load_dotenv()

    finder = FoodCarbFinder(api_key=os.getenv("USDA_API_KEY"))

    desc, carbs = finder.get_carbs("apple pie")
    print(f"\n{desc}")
    print(f"Carbs per 100g: {carbs['per_100g']} g")
    for s in carbs["per_serving"]:
        print(f"- {s['measure']} ({s['gram_weight']} g): {s['carbs']} g carbs")

    desc, carbs = finder.get_carbs("red delicious apple", exact=True)
    print(f"\n{desc}")
    print(f"Carbs per 100g: {carbs['per_100g']} g")
    for s in carbs["per_serving"]:
        print(f"- {s['measure']} ({s['gram_weight']} g): {s['carbs']} g carbs")
