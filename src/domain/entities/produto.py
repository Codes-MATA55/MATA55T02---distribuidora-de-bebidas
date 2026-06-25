class Product:
    def __init__(
        self,
        id: str,
        brand: str,
        name: str,
        description: str,
        barcode: str,
        price: float,
        amount_stock: int,
        supplier: str
    ):
        
        if not id or not id.strip():
            raise ValueError("Id é obrigatório")   
             
        if not brand or not brand.strip():
            raise ValueError("Marca é obrigatória")

        if not name or not name.strip():
            raise ValueError("Nome é obrigatório")

        if price < 0:
            raise ValueError("Preço não pode ser negativo")

        if amount_stock < 0:
            raise ValueError("amount em estoque não pode ser negativa")

        self._id = id.strip()
        self._brand = brand.strip()
        self._name = name.strip()
        self._description = description.strip()
        self._barcode = barcode.strip()
        self._price = price
        self._amount_stock = amount_stock
        self._supplier = supplier

    @property
    def id(self):
        return self._id

    @property
    def brand(self):
        return self._brand

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def barcode(self):
        return self._barcode

    @property
    def barcode(self):
        return self.barcode

    @property
    def price(self):
        return self._price

    @property
    def amount_stock(self):
        return self._amount_stock

    @property
    def qtestoque(self):
        return self.amount_stock

    @property
    def supplier(self):
        return self._supplier

    def add_stock(self, amount: int):
        if amount <= 0:
            raise ValueError("A quantidade a adicionar deve ser maior que zero")

        self._amount_stock += amount

    def remove_stock(self, amount: int):
        if amount <= 0:
            raise ValueError("A quantidade a remover deve ser maior que zero")

        if amount > self._amount_stock:
            raise ValueError("Saldo insuficiente em estoque")

        self._amount_stock -= amount

    def decrease_stock(self, amount: int):
        self.remove_stock(amount)

    def change_price(self, new_price: float):
        if new_price < 0:
            raise ValueError("Preço não pode ser negativo")

        self._price = new_price

    def change_description(self, new_description: str):
        if not new_description or not new_description.strip():
            raise ValueError("Descrição não pode ser vazia")

        self._description = new_description.strip()
