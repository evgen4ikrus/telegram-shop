def create_product_description(product):
    description = product.get('attributes').get('description')
    title = product.get('attributes').get('name')
    price = product.get('attributes').get('price').get('USD').get('amount') * 0.01
    text = f"{title}\n\n{price}$ за кг.\n\n{description}"
    return text


def create_cart_description(cart_items):
    cart_description = ''
    total_price = 0
    for item in cart_items:
        one_for_price = item.get('unit_price').get('amount') * 0.01
        price = one_for_price * item.get("quantity")
        total_price += price
        title = item.get('name')
        description = item.get('description')
        quantity = item.get('quantity')
        cart_description += f"{title}\n{description}\n{quantity}кг. за {price}$ ({one_for_price}$ за кг.)\n\n"
    cart_description += f'Общая цена: {total_price}$'
    return cart_description
