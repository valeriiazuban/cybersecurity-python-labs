
USERS = {
    "blockchain_dev": {
        "role": "blockchain_developer",
        "clearance": 3,
        "department": "Blockchain",
        "active": True,
    },
    "smart_contract_auditor": {
        "role": "contract_auditor",
        "clearance": 3,
        "department": "Audit",
        "active": True,
    },
    "crypto_trader": {
        "role": "trader",
        "clearance": 2,
        "department": "Trading",
        "active": True,
    },
    "wallet_user": {
        "role": "wallet_user",
        "clearance": 1,
        "department": "Users",
        "active": True,
    },
    "mining_pool": {
        "role": "miner",
        "clearance": 1,
        "department": "Mining",
        "active": False,
    },
}

RESOURCES = [
    ("smart_contracts", 3),
    ("audit_reports", 3),
    ("trading_algorithms", 2),
    ("wallet_interface", 1),
    ("private_keys", 3),
    ("public_blockchain", 1),
    ("defi_protocols", 3),
    ("validator_nodes", 3),
    ("market_data", 2),
    ("community_forum", 1),
]

SECURITY_LEVELS = (
    "Public Blockchain",
    "Permissioned",
    "Private Network",
    "Institutional",
)

BLOCKED_USERS = {"flash_loan_attack", "rug_pull_scam"}


def check_resource_access(
    username: str, resource_name: str, resource_req_level: int
) -> tuple[bool, str]:
    """Перевіряє можливість доступу користувача до ресурсу."""
    #Перевірка на список заблокованих
    if username in BLOCKED_USERS:
        return False, "Користувач у списку заблокованих (BLOCKED_USERS)"

    #Перевірка існування користувача
    user_data = USERS.get(username)
    if not user_data:
        return False, "Користувач не знайдений у системі"

    # Перевірка активності акаунта
    if not user_data.get("active", False):
        return False, "Акаунт деактивований (active=False)"

    # Перевірка рівня допуску clearance
    user_clearance = user_data.get("clearance", 0)
    if user_clearance >= resource_req_level:
        return True, f"Доступ дозволено (Допуск {user_clearance} >= {resource_req_level})"

    return False, f"Недостатній рівень допуску ({user_clearance} < {resource_req_level})"