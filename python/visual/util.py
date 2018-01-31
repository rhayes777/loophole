def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    if old_value > old_range_max:
        old_value = old_range_max
    if old_value < old_range_min:
        old_value = old_range_min
    return (old_value - old_range_min) * (new_range_max - new_range_min) / (
            old_range_max - old_range_min) + new_range_min
