from django import template
from django.template.loader import get_template

def left_menu():
	return {}

register = template.Library()
t = get_template('med/left_menu.html')
register.inclusion_tag(t)(left_menu)
