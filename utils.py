def split_full_name(full_name):
    """Разбивает ФИО на (имя, фамилия, отчество)."""
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], "", ""
    if len(parts) == 2:
        return parts[0], parts[1], ""
    return parts[1], parts[0], parts[2]