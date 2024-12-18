import pytest
from main import TextAdventureGame, CombatEntity


@pytest.fixture
def game():
    """Фикстура для создания нового экземпляра игры перед каждым тестом."""
    return TextAdventureGame()


@pytest.fixture
def player():
    """Фикстура для создания объекта игрока."""
    return CombatEntity("Игрок", health=100, attack=10, defense=5)


@pytest.fixture
def enemy():
    """Фикстура для создания врага."""
    return CombatEntity("Гоблин", health=50, attack=8, defense=2)


def test_initial_location(game):
    """Тест начального состояния локации."""
    assert game.current_location == "forest"
    assert game.get_description() == "Вы в лесу. Можно идти на север или собирать ресурсы."


def test_valid_action_collect_resources(game):
    """Тест на успешный сбор ресурсов."""
    result = game.take_action("Собирать ресурсы")
    assert "Вы собрали" in result
    assert game.inventory["ресурсы"] > 0


def test_valid_action_travel(game):
    """Тест на переход в новую локацию."""
    result = game.take_action("Идти на север")
    assert result == "Вы в пещере. Здесь темно и опасно."
    assert game.current_location == "cave"


def test_invalid_action(game):
    """Тест на выполнение недопустимого действия."""
    result = game.take_action("Неправильное действие")
    assert result == "Недопустимое действие!"


def test_combat_entity_damage(player):
    """Тест на получение урона сущностью."""
    damage_taken = player.take_damage(15)
    assert damage_taken == 10
    assert player.health == 90


def test_combat_entity_survival(player):
    """Тест проверки жив ли объект."""
    player.take_damage(120)
    assert not player.is_alive()


@pytest.mark.parametrize(
    "action,expected_location",
    [
        ("Собирать ресурсы", "forest"),
        ("Идти на север", "cave"),
    ]
)
def test_parametrized_location_transitions(game, action, expected_location):
    """Параметризованный тест переходов между локациями."""
    game.take_action(action)
    assert game.current_location == expected_location


def test_encounter_enemy_chance(monkeypatch, game):
    """Тест на вероятность появления врага."""

    def mock_random():
        return 0.1

    monkeypatch.setattr("random.random", mock_random)
    enemy = game.encounter_enemy()
    assert enemy is not None
    assert enemy.name == "Гоблин"


def test_encounter_no_enemy_chance(monkeypatch, game):
    """Тест на отсутствие врага."""

    def mock_random():
        return 0.9

    monkeypatch.setattr("random.random", mock_random)
    enemy = game.encounter_enemy()
    assert enemy is None


@pytest.mark.parametrize(
    "damage,expected_health",
    [
        (20, 85),
        (5, 100),
        (100, 5),
    ]
)
def test_parametrized_combat_damage(player, damage, expected_health):
    """Параметризованный тест на урон в бою."""
    player.take_damage(damage)
    assert player.health == expected_health


def test_full_combat_simulation(player, enemy):
    """Тест на полное моделирование боя."""
    while player.is_alive() and enemy.is_alive():
        damage_to_enemy = player.attack
        enemy.take_damage(damage_to_enemy)

        if enemy.is_alive():
            damage_to_player = enemy.attack
            player.take_damage(damage_to_player)

    assert player.is_alive() or not enemy.is_alive()
    assert not enemy.is_alive()
