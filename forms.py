from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    """Форма с разными типами данных."""
    field1_str = State()
    field2_int = State()
    field3_choice = State()
