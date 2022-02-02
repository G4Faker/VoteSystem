from django import template


register = template.Library()


def int_pow(value, power):
    return int(value) ** int(power)


def check_includes(value, array):
    for item in array:
        if str(item.user.username) == str(value):
            return True
    return False


register.filter('int_pow', int_pow)
register.filter('check_includes', check_includes)
