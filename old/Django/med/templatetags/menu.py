from django import template
from django.template.loader import get_template

def left_menu():
	return {}

def get_item(dictionary, key):
    return dictionary.get(key)

register = template.Library()
t = get_template('med/left_menu.html')
register.inclusion_tag(t)(left_menu)
register.filter('get_item', get_item)
