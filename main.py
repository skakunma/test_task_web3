from web3 import Web3
from os import environ

# Подключение к Infura
infura_url = environ.get('infura_url') #переменные окружения .env
web3 = Web3(Web3.HTTPProvider(infura_url))

# ABI для Uniswap V2 Factory
uniswap_factory_abi = [
    {
        "constant": True,
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"}
        ],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

# ABI для Uniswap V2 Pair
uniswap_pair_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]


def main():
    # Проверка подключения
    if not web3.is_connected():
        print("Не удалось подключиться к Ethereum")
        exit()

    # Адрес Uniswap V2 Factory
    uniswap_factory_address = environ.get('uniswap_factory_address')#переменные окружения в .env


    # Создание контрактного объекта для Factory
    factory_contract = web3.eth.contract(address=uniswap_factory_address, abi=uniswap_factory_abi)

    # Адреса токенов (WETH и USDT)
    weth_address = web3.to_checksum_address('0xC02aaa39b223FE8D0a0e5C4F27ead9083C756Cc2')
    usdt_address = web3.to_checksum_address('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606EB48')

    # Получение адресов пулов для пары WETH/USDT
    pool1_address = factory_contract.functions.getPair(weth_address, usdt_address).call()
    pool2_address = factory_contract.functions.getPair(usdt_address, weth_address).call()

    # Приведение адресов к Checksum формату
    pool1_address = web3.to_checksum_address(pool1_address)
    pool2_address = web3.to_checksum_address(pool2_address)

    # Создание контрактных объектов для пулов
    pool1_contract = web3.eth.contract(address=pool1_address, abi=uniswap_pair_abi)
    pool2_contract = web3.eth.contract(address=pool2_address, abi=uniswap_pair_abi)

    def get_price(pool_contract):
        reserves = pool_contract.functions.getReserves().call()
        reserve_eth = reserves[0]  # Резерв ETH (WETH)
        reserve_usdt = reserves[1]  # Резерв USDT
        price = reserve_usdt / reserve_eth
        return price

    # Получение цен из пулов
    price_pool1 = get_price(pool1_contract)
    price_pool2 = get_price(pool2_contract)

    # Расчет разницы в цене
    price_difference = abs(price_pool1 - price_pool2) / ((price_pool1 + price_pool2) / 2) * 100

    # Вывод результатов
    print(f"Адрес пула 1: {pool1_address}")
    print(f"Цена ETH/USDT в пуле 1: {price_pool1}")
    print(f"Адрес пула 2: {pool2_address}")
    print(f"Цена ETH/USDT в пуле 2: {price_pool2}")
    print(f"Разница в цене: {price_difference:.2f}%")

    if price_difference > 0.5:
        print("Возможна арбитражная возможность!")


if __name__ == '__main__':
    while True:
        main()