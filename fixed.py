import random
import pygame
import tkinter as tk
from tkinter import simpledialog, messagebox

# Node class for Skip List
class PlayerNode:
    """Node for each player in the skip list, storing player name, time, and level links."""
    def __init__(self, player, time, level):
        self.player = player  # Player name
        self.time = time      # Best race time
        self.forward = [None] * (level + 1)  # Forward pointers for each level
        self.level = level    # Node level

# Skip List implementation
class SkipList:
    """Skip list data structure for storing player nodes sorted by time or name."""
    def __init__(self, max_level, p, sort_key):
        self.MAX_LEVEL = max_level  # Maximum level of skip list
        self.P = p                  # Probability factor for level generation
        self.sort_key = sort_key    # Sorting criteria ('time' or 'player')
        self.header = self.create_node("-INF", float('-inf'), self.MAX_LEVEL)  # Header node
        self.level = 0
        self.nodes = {}  # Dictionary to store nodes by player name

    def create_node(self, player, time, level):
        return PlayerNode(player, time, level)

    def random_level(self):
        #this is basically deciding kay konsa player mmoves up in the ladder/skiplisy
        lvl = 0
        while random.random() < self.P and lvl < self.MAX_LEVEL: 
            lvl += 1
        return lvl

    # Insert or update a player's time
    def insert(self, player, time):
        if player in self.nodes:
            self._delete_node(player)  # Remove existing node if player exists
        update = [None] * (self.MAX_LEVEL + 1) #The update list remembers where to adjust the pointers (links) on each level when you insert a new player.
        current = self.header
        # Find position to insert
        for i in reversed(range(self.level + 1)):
            while current.forward[i] and self.compare(current.forward[i], player, time) < 0:
                current = current.forward[i]
            update[i] = current
            #Keep moving forward until you find where this player should be placed on that level. Once you find it, mark that spot in your helper list (update[i]).
        rlevel = self.random_level()
        if rlevel > self.level:
            for i in range(self.level + 1, rlevel + 1):
                update[i] = self.header
            self.level = rlevel
        new_node = self.create_node(player, time, rlevel)
        self.nodes[player] = new_node
        for i in range(rlevel + 1): #connect to peechay and agay wala node 
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

    # Comparison logic based on sort_key
    #It compares two players to see who comes first in the skip list/depenidng on the sorting criteria (time or name).
    def compare(self, node, player, time):
        if self.sort_key == 'time':
            return -1 if node.time < time else (1 if node.time > time else 0) 
        else:
            return -1 if node.player < player else (1 if node.player > player else 0)
        #using this in delete and insert to see if the player is ahead or behind in the list.

    def search(self, player):
        current = self.header
        for i in reversed(range(self.level + 1)):  # Start from top level
            while current.forward[i] and self.compare(current.forward[i], player, current.forward[i].time) < 0:
                current = current.forward[i]
        current = current.forward[0]  # Move to possible target at level 0
        if current and current.player == player:
            return current
        return None


    # Delete a player from skip list
    def _delete_node(self, player):
        update = [None] * (self.MAX_LEVEL + 1)
        current = self.header
        target_time = self.nodes[player].time
        #You grab a helper list (update) to remember where to fix the links.
        for i in reversed(range(self.level + 1)):
            while current.forward[i] and self.compare(current.forward[i], player, target_time) < 0:
                current = current.forward[i]
            update[i] = current
            #Keep moving forward until you're standing right before the player you want to delete
            #Once you're there, mark that spot in update[i] so you remember where to fix links later
        target = current.forward[0]
        if target and target.player == player:
            for i in range(len(target.forward)):
                if update[i].forward[i] == target:
                    update[i].forward[i] = target.forward[i]
                    #for every levl, you tell the previous node to skip over the one you're deleting and point to the next one instead.
            while self.level > 0 and self.header.forward[self.level] is None:
                self.level -= 1
            del self.nodes[player]
            #If the top floor becomes empty, you remove that floor by lowering the skip list’s level.

    # Return leaderboard sorted by time
    def get_leaderboard(self):
        result = []
        current = self.header.forward[0] #Start at the first player on Level 0 
        while current:
            result.append((current.player, current.time)) #Write down their name and best time in your notebook (the result list).
            current = current.forward[0] #Move to the next player in line on Level 0
        return result

# Draw a simple car using pygame shapes
def draw_car(screen, x, y, color):
    """Draws a simple car shape at the given x, y position."""
    pygame.draw.rect(screen, color, (x, y, 30, 15))  # Car body
    pygame.draw.rect(screen, (200, 200, 200), (x + 5, y - 8, 20, 8))  # Roof
    pygame.draw.circle(screen, (0, 0, 0), (x + 5, y + 15), 3)  # Left wheel
    pygame.draw.circle(screen, (0, 0, 0), (x + 25, y + 15), 3)  # Right wheel

# Run the racing simulation
def run_race(players, best_times, time_skiplist, player_skiplist):
    """Runs a race simulation for players and updates their best times in skip lists."""
    def wait_for_space():
        # Wait for user to press SPACE to start race
        waiting = True
        font = pygame.font.SysFont(None, 40)
        text = font.render("Press SPACE to Start", True, (255, 255, 255))
        while waiting:
            screen.fill((50, 50, 50))
            screen.blit(text, (80, 280))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False

    pygame.init() # thsi starts the race 
    screen = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("Vertical Racing Game")
    clock = pygame.time.Clock()

    wait_for_space()  # Wait for user input

    lane_width = 400 // len(players)  # Adjust lanes dynamically
    positions = {player: 550 for player in players}  # Starting positions
    speeds = {player: random.uniform(2, 5) for player in players}  # Random speeds
    colors = [(random.randint(50,255), random.randint(50,255), random.randint(50,255)) for _ in players]  # Random car colors

    running = True
    while running:
        screen.fill((100, 100, 100))  # Background
        for i in range(1, len(players) + 1):
            pygame.draw.line(screen, (255, 255, 255), (i*lane_width, 0), (i*lane_width, 600), 2)  # Draw lanes
        for idx, player in enumerate(players):
            positions[player] -= speeds[player]  # Move cars upward
            x_pos = idx * lane_width + 5
            draw_car(screen, x_pos, positions[player], colors[idx])  # Draw each car
        pygame.display.flip()
        clock.tick(60)
        if all(pos < 0 for pos in positions.values()):
            running = False
    pygame.quit()

    # Record race times
    for player in players:
        time = round(random.uniform(1.0, 5.0), 2)
        if player not in best_times or time < best_times[player]:
            best_times[player] = time
            time_skiplist.insert(player, time)
            player_skiplist.insert(player, time)

# Visualize the skip list structure
def visualize_skiplist(skiplist):
    """Visualizes the skip list using Pygame, showing each level and node."""
    pygame.init()
    screen = pygame.display.set_mode((1200, 700))
    pygame.display.set_caption("Skip List Visualization")
    font = pygame.font.SysFont(None, 26)
    screen.fill((30, 30, 30))  # Background color
    y_start = 80
    level_gap = 130
    node_radius = 30
    max_width = 1000
    for lvl in range(skiplist.level, -1, -1):
        y = y_start + (skiplist.level - lvl) * level_gap
        node = skiplist.header.forward[lvl]
        len_nodes = 0
        temp = node
        while temp:
            len_nodes += 1
            temp = temp.forward[lvl]
        node_gap = min(140, max_width // (len_nodes + 1))  # Dynamic gap based on node count
        if len_nodes > 0:
            first_x = 120
            last_x = first_x + (len_nodes - 1) * node_gap + node_radius
            pygame.draw.line(screen, (200, 200, 200), (first_x - node_radius, y + node_radius), (last_x + 40, y + node_radius), 2)
        level_label = font.render(f'Level {lvl}', True, (255, 255, 255))
        screen.blit(level_label, (20, y + node_radius - 12))
        x = 120
        while node:
            pygame.draw.circle(screen, (0, 122, 255), (x, y + node_radius), node_radius)  # Draw node
            player_label = font.render(f"P{node.player[6:]}", True, (255, 255, 255))  # Player label
            time_label = font.render(f"{node.time:.2f}s", True, (200, 200, 200))  # Time label
            screen.blit(player_label, (x - 8, y + node_radius - 10))
            screen.blit(time_label, (x - 28, y + node_radius + 32))
            if node.forward[lvl]:
                pygame.draw.line(screen, (255, 255, 255), (x + node_radius, y + node_radius), (x + node_gap - node_radius, y + node_radius), 2)  # Connect nodes
            x += node_gap
            node = node.forward[lvl]
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
    pygame.quit()

# GUI to interact with the leaderboard
def launch_gui(time_skiplist, player_skiplist):
    """Launches a Tkinter GUI for leaderboard interaction with refresh, search, delete, and top N features."""
    def refresh_leaderboard():
        leaderboard = time_skiplist.get_leaderboard()
        text.delete('1.0', tk.END)
        for idx, (player, t) in enumerate(leaderboard, 1):
            text.insert(tk.END, f"{idx}. {player} - {t:.2f}s\n")

    def search_player():
        name = simpledialog.askstring("Search Player", "Enter player name(case sensitive):")
        node = player_skiplist.search(name)
        if node:
            leaderboard = time_skiplist.get_leaderboard()
            position = next((idx + 1 for idx, (p, _) in enumerate(leaderboard) if p == name), 'N/A')
            messagebox.showinfo("Found", f"{name}'s best time: {node.time:.2f}s\nCurrent Position: {position}")
        else:
            messagebox.showerror("Not Found", f"{name} not in leaderboard.")

    def delete_player():
        name = simpledialog.askstring("Delete Player", "Enter player name(case sensitive):")
        node = player_skiplist.search(name)
        if node:
            time_skiplist._delete_node(name)
            player_skiplist._delete_node(name)
            refresh_leaderboard()
            messagebox.showinfo("Deleted", f"{name} removed.")
        else:
            messagebox.showerror("Not Found", f"{name} not in leaderboard.")

    def show_top_n():
        try:
            n = int(simpledialog.askstring("Top N", "Enter N:"))
            leaderboard = time_skiplist.get_leaderboard()[:n]
            text.delete('1.0', tk.END)
            for idx, (player, t) in enumerate(leaderboard, 1):
                text.insert(tk.END, f"{idx}. {player} - {t:.2f}s\n")
        except ValueError:
            messagebox.showerror("Error", "Invalid number.")

    root = tk.Tk()
    root.title("Leaderboard")
    text = tk.Text(root, height=15, width=30)
    text.pack()
    tk.Button(root, text="Refresh Leaderboard", command=refresh_leaderboard).pack()
    tk.Button(root, text="Search Player", command=search_player).pack()
    tk.Button(root, text="Delete Player", command=delete_player).pack()
    tk.Button(root, text="Show Top N", command=show_top_n).pack()
    tk.Button(root, text="Exit", command=root.destroy).pack()
    refresh_leaderboard()
    root.mainloop()

# Main execution
if __name__ == "__main__":
    max_level = 4
    probability = 0.5
    players = [f"Player{i+1}" for i in range(12)]  # Generate 12 players
    time_skiplist = SkipList(max_level, probability, sort_key='time')  # Skip list sorted by time
    player_skiplist = SkipList(max_level, probability, sort_key='player')  # Skip list sorted by name
    best_times = {}
    run_race(players, best_times, time_skiplist, player_skiplist)  # Start race
    visualize_skiplist(time_skiplist)  # Show skip list
    launch_gui(time_skiplist, player_skiplist)  # Launch leaderboard GUI
