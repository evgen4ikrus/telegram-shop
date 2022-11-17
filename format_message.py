# Доделать получение цены и передать сообщение при клике на товар
def create_product_description(product):
    text = f'''{product.get('attributes').get('name')}\n
{product.get('attributes').get('description')}'''
    return text


def create_cart_description(cart_items):
    cart_description = ''
    total_price = 0
    for item in cart_items:
        one_for_price = item.get('unit_price').get('amount') * 0.01
        price = one_for_price * item.get("quantity")
        total_price += price
        cart_description += f'''{item.get("name")}
{item.get("description")}
{item.get("quantity")}шт. за {price}$ ({one_for_price}$ за шт.)\n\n'''
    cart_description += f'Общая цена: {total_price}$'
    return cart_description
