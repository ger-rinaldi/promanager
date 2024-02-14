from app.validation.requirements import max_budget, min_budget


def budget_amount(budget) -> bool:
    if not min_budget < float(budget) < max_budget:
        return False

    return True
