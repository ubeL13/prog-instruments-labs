# text_adventure_gui.py

import tkinter as tk
from tkinter import messagebox
import random


class CombatEntity:
    """Базовый класс для игрока и врагов."""
    def __init__(self, name, health, attack, defense):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense

    def take_damage(self, damage):
        """Уменьшает здоровье, учитывая защиту."""
        damage_taken = max(damage - self.defense, 0)
        self.health -= damage_taken
        return damage_taken

    def is_alive(self):
        return self.health > 0


class TextAdventureGame:
    """Логика текстового приключения."""
    def __init__(self):
        self.locations = {
            "forest": {
                "description": "Вы в лесу. Можно идти на север или собирать ресурсы.",
                "actions": ["Собирать ресурсы", "Идти на север"],
                "next": {"Собирать ресурсы": "forest", "Идти на север": "cave"},
                "enemy_chance": 0.2
            },
            "cave": {
                "description": "Вы в пещере. Здесь темно и опасно.",
                "actions": ["Идти к озеру", "Вернуться назад"],
                "next": {"Идти к озеру": "lake", "Вернуться назад": "forest"},
                "enemy_chance": 0.4
            },
            "lake": {
                "description": "Вы у озера. Можно собрать воду или построить плот.",
                "actions": ["Собрать воду", "Построить плот"],
                "next": {"Собрать воду": "lake", "Построить плот": "win"},
                "enemy_chance": 0.0
            },
            "win": {
                "description": "Вы построили плот и уплыли на свободу! Поздравляем, вы победили!",
                "actions": []
            }
        }
        self.current_location = "forest"
        self.player = CombatEntity("Игрок", health=100, attack=10, defense=5)
        self.inventory = {"ресурсы": 0, "вода": 0}

    def get_description(self):
        return self.locations[self.current_location]["description"]

    def get_actions(self):
        return self.locations[self.current_location]["actions"]

    def take_action(self, action):
        if action not in self.get_actions():
            return "Недопустимое действие!"

        if action == "Собирать ресурсы":
            resources = random.randint(1, 3)
            self.inventory["ресурсы"] += resources
            return f"Вы собрали {resources} ресурса(-ов). У вас {self.inventory['ресурсы']} ресурсов."

        if action == "Собрать воду":
            self.inventory["вода"] += 1
            return f"Вы набрали воду. У вас {self.inventory['вода']} ед. воды."

        if action == "Построить плот":
            if self.inventory["ресурсы"] >= 5 and self.inventory["вода"] >= 1:
                self.current_location = "win"
                return self.get_description()
            return "Для постройки плота нужно 5 ресурсов и 1 вода."

        # Проверка перехода между локациями
        next_location = self.locations[self.current_location]["next"].get(action, self.current_location)
        self.current_location = next_location
        return self.get_description()

    def encounter_enemy(self):
        """Проверяет, встретил ли игрок врага."""
        enemy_chance = self.locations[self.current_location].get("enemy_chance", 0)
        if random.random() < enemy_chance:
            return CombatEntity("Гоблин", health=50, attack=8, defense=2)
        return None


class TextAdventureApp:
    """Графический интерфейс для игры."""
    def __init__(self, root):
        self.game = TextAdventureGame()
        self.root = root
        self.root.title("Text Adventure Game")

        # Описание локации
        self.description_label = tk.Label(root, text=self.game.get_description(), wraplength=400, font=("Arial", 14))
        self.description_label.pack(pady=10)

        # Кнопки для действий
        self.action_buttons_frame = tk.Frame(root)
        self.action_buttons_frame.pack(pady=10)

        # Статус игрока
        self.status_label = tk.Label(root, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)

        # Обновление интерфейса
        self.update_ui()

    def update_ui(self):
        """Обновляет текст и кнопки в интерфейсе."""
        self.description_label.config(text=self.game.get_description())
        self.status_label.config(
            text=f"Здоровье: {self.game.player.health} | Ресурсы: {self.game.inventory['ресурсы']} | Вода: {self.game.inventory['вода']}"
        )

        # Удаляем старые кнопки
        for widget in self.action_buttons_frame.winfo_children():
            widget.destroy()

        # Добавляем новые кнопки
        actions = self.game.get_actions()
        for action in actions:
            btn = tk.Button(self.action_buttons_frame, text=action, command=lambda a=action: self.perform_action(a))
            btn.pack(fill="x", pady=5)

    def perform_action(self, action):
        """Обрабатывает выбор действия игрока."""
        # Проверяем на встречу с врагом
        enemy = self.game.encounter_enemy()
        if enemy:
            self.start_combat(enemy)
            return

        # Выполняем действие
        result = self.game.take_action(action)
        messagebox.showinfo("Действие", result)

        # Проверяем состояние игрока
        if self.game.player.health <= 0:
            messagebox.showerror("Игра окончена", "Вы погибли. Начните заново.")
            self.root.destroy()
            return

        # Обновляем интерфейс
        self.update_ui()

    def start_combat(self, enemy):
        """Начинает бой с врагом."""
        combat_window = tk.Toplevel(self.root)
        combat_window.title("Бой с врагом")

        tk.Label(combat_window, text=f"Враг: {enemy.name} | Здоровье: {enemy.health}", font=("Arial", 12)).pack(pady=10)
        tk.Label(combat_window, text=f"Ваше здоровье: {self.game.player.health}", font=("Arial", 12)).pack(pady=10)

        def attack_enemy():
            """Атака врага."""
            damage = self.game.player.attack
            taken = enemy.take_damage(damage)
            messagebox.showinfo("Бой", f"Вы нанесли {taken} урона врагу.")
            if not enemy.is_alive():
                messagebox.showinfo("Победа", "Вы победили врага!")
                combat_window.destroy()
            else:
                self.enemy_attack(enemy)

        tk.Button(combat_window, text="Атаковать", command=attack_enemy).pack(fill="x", pady=5)

    def enemy_attack(self, enemy):
        """Враг атакует игрока."""
        damage = enemy.attack
        taken = self.game.player.take_damage(damage)
        messagebox.showwarning("Бой", f"Враг атаковал и нанес {taken} урона!")
        if self.game.player.health <= 0:
            messagebox.showerror("Игра окончена", "Вы погибли в бою.")
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TextAdventureApp(root)
    root.mainloop()
