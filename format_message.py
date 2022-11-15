# Доделать получение цены и передать сообщение при клике на товар
def create_product_description(product):
    text = f'''{product.get('attributes').get('name')}\n
{product.get('attributes').get('description')}'''
    return text
