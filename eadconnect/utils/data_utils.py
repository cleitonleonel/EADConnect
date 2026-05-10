from datetime import date, timedelta
from typing import Tuple


def get_current_month_range() -> Tuple[str, str]:
    """
    Obtém o intervalo de datas do mês atual, do primeiro dia até o início do próximo mês mais 30 dias.

    Retorna:
        Tuple[str, str]: Uma tupla contendo a data de início (YYYY-MM-DD) e a data de término (formato ISO 8601).
    """
    today = date.today()
    start_date = today.replace(day=1)
    
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
        
    end_date = next_month + timedelta(days=30)

    return today.strftime("%Y-%m-%d"), end_date.isoformat()
