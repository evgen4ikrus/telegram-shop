# Доделать получение цены и передать сообщение при клике на товар
def create_product_description(product):
    text = f'''{product.get('attributes').get('name')}\n
{product.get('attributes').get('description')}'''
    return text


# Доделать получение цены и передать красивое содержимое корзины
def create_cart_description(cart_items):
    description = ''
    for item in cart_items:
        description += f'{item.get("name")}\n{item.get("description")}\n\n'
    return description
