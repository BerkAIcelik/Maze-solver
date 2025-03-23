import numpy as np
import random
import pygame

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False
        self.in_maze = False  # Prim algoritması için
        self.is_start = False
        self.is_end = False
        self.is_path = False
        self.is_solution = False
        self.distance = float('inf')  # Dijkstra ve A* için
        self.heuristic = 0  # A* için
        self.parent = None  # Çözüm yolunu yeniden oluşturmak için
        
    def reset_path_data(self):
        self.visited = False
        self.is_path = False
        self.is_solution = False
        self.distance = float('inf')
        self.parent = None
    
    def get_neighbors(self, grid, include_walls=False):
        neighbors = []
        rows, cols = len(grid), len(grid[0])
        directions = [("top", -1, 0), ("right", 0, 1), ("bottom", 1, 0), ("left", 0, -1)]
        
        for direction, dr, dc in directions:
            nr, nc = self.row + dr, self.col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor_cell = grid[nr][nc]
                # Bu yönde duvar yoksa veya duvarları dahil etmek istiyorsak komşuyu ekleyelim
                if not self.walls[direction] or include_walls:
                    neighbors.append(neighbor_cell)
        
        return neighbors

class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[Cell(i, j) for j in range(cols)] for i in range(rows)]
        self.current_cell = None
        self.stack = []  # Recursive Backtracking için
        self.frontier = []  # Prim algoritması için
        self.generation_algorithm = "recursive_backtracking"
        self.generation_complete = False
        self.start_cell = None
        self.end_cell = None
        
        # Başlangıç ve bitiş hücrelerini ayarla
        self.start_cell = self.grid[0][0]
        self.start_cell.is_start = True
        self.end_cell = self.grid[rows-1][cols-1]
        self.end_cell.is_end = True
    
    def set_generation_algorithm(self, algorithm):
        self.generation_algorithm = algorithm
        self.generation_complete = False
        self.reset_maze()
        
        if algorithm == "recursive_backtracking":
            self.prepare_recursive_backtracking()
        elif algorithm == "prims_algorithm":
            self.prepare_prims_algorithm()
            
    def reset_maze(self):
        # Tüm hücreleri sıfırla
        for row in self.grid:
            for cell in row:
                cell.walls = {"top": True, "right": True, "bottom": True, "left": True}
                cell.visited = False
                cell.in_maze = False
                cell.reset_path_data()
        
        # Başlangıç ve bitiş hücrelerini yeniden ayarla
        self.start_cell = self.grid[0][0]
        self.start_cell.is_start = True
        self.end_cell = self.grid[self.rows-1][self.cols-1]
        self.end_cell.is_end = True
        
        self.stack = []
        self.frontier = []
    
    def prepare_recursive_backtracking(self):
        # Başlangıç hücresini seç
        self.current_cell = self.grid[0][0]
        self.current_cell.visited = True
        self.stack.append(self.current_cell)
    
    def prepare_prims_algorithm(self):
        # Başlangıç hücresini seç ve labirente ekle
        start_row, start_col = 0, 0
        self.grid[start_row][start_col].in_maze = True
        
        # Başlangıç hücresinin sınır komşularını ekle
        self.add_frontier_neighbors(start_row, start_col)
    
    def add_frontier_neighbors(self, row, col):
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.grid[nr][nc].in_maze and not self.grid[nr][nc] in self.frontier:
                self.frontier.append(self.grid[nr][nc])
    
    def remove_wall_between(self, current, next_cell):
        # İki hücre arasındaki duvarı kaldır
        dx = next_cell.col - current.col
        dy = next_cell.row - current.row
        
        if dx == 1:  # next_cell sağda
            current.walls["right"] = False
            next_cell.walls["left"] = False
        elif dx == -1:  # next_cell solda
            current.walls["left"] = False
            next_cell.walls["right"] = False
        elif dy == 1:  # next_cell aşağıda
            current.walls["bottom"] = False
            next_cell.walls["top"] = False
        elif dy == -1:  # next_cell yukarıda
            current.walls["top"] = False
            next_cell.walls["bottom"] = False
    
    def generate_step(self):
        if self.generation_complete:
            return True
        
        if self.generation_algorithm == "recursive_backtracking":
            return self.recursive_backtracking_step()
        elif self.generation_algorithm == "prims_algorithm":
            return self.prims_algorithm_step()
        
        return False
    
    def recursive_backtracking_step(self):
        if not self.stack:
            self.generation_complete = True
            return True
        
        self.current_cell = self.stack[-1]
        
        # Tüm komşuları kontrol et (hücreler arasındaki duvarlar dahil)
        unvisited_neighbors = []
        row, col = self.current_cell.row, self.current_cell.col
        directions = [("top", -1, 0), ("right", 0, 1), ("bottom", 1, 0), ("left", 0, -1)]
        
        for direction, dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and not self.grid[nr][nc].visited:
                unvisited_neighbors.append((direction, self.grid[nr][nc]))
        
        if unvisited_neighbors:
            # Rastgele bir komşu seç
            direction, next_cell = random.choice(unvisited_neighbors)
            
            # Duvarı kaldır
            self.remove_wall_between(self.current_cell, next_cell)
            
            # Yeni hücreyi işaretle ve yığına ekle
            next_cell.visited = True
            self.stack.append(next_cell)
            self.current_cell = next_cell
        else:
            # Geri izleme
            self.stack.pop()
        
        return False
    
    def prims_algorithm_step(self):
        if not self.frontier:
            self.generation_complete = True
            return True
        
        # Rastgele bir sınır hücresi seç
        current_index = random.randint(0, len(self.frontier) - 1)
        current = self.frontier.pop(current_index)
        
        # Labirentteki komşuları bul
        maze_neighbors = []
        directions = [("top", -1, 0), ("right", 0, 1), ("bottom", 1, 0), ("left", 0, -1)]
        
        for direction, dr, dc in directions:
            nr, nc = current.row + dr, current.col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc].in_maze:
                maze_neighbors.append((direction, self.grid[nr][nc]))
        
        if maze_neighbors:
            # Rastgele bir labirent komşusu seç
            direction, maze_neighbor = random.choice(maze_neighbors)
            
            # Duvarı kaldır
            self.remove_wall_between(current, maze_neighbor)
            
            # Hücreyi labirente ekle
            current.in_maze = True
            
            # Yeni hücrenin sınır komşularını ekle
            self.add_frontier_neighbors(current.row, current.col)
            
            self.current_cell = current
        
        return False
    
    def draw(self, screen, cell_size, offset_x=0, offset_y=0):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]
                x = col * cell_size + offset_x
                y = row * cell_size + offset_y
                
                # Arka plan rengini belirle
                color = (0, 0, 0)  # Arka plan siyah
                
                if cell.is_solution:
                    # Çözüm yolundaki hücreler sarı
                    color = (255, 255, 0)  # Sarı
                elif cell.visited:
                    # Ziyaret edilmiş hücreler için kırmızının %40 opaklıktaki tonu
                    color = (102, 0, 0)  # Kırmızının %40 opaklıktaki tonu
                elif not self.generation_complete and self.generation_algorithm == "prims_algorithm":
                    if cell.in_maze:
                        # Prim algoritmasında labirente eklenmiş hücreler için kırmızının %40 opaklıktaki tonu
                        color = (102, 0, 0)  # Kırmızının %40 opaklıktaki tonu
                
                # Hücre arka planını çiz
                pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))
                
                # Prim algoritması için sınır hücrelerini farklı bir renkte göster (sadece oluşum aşamasında)
                if not self.generation_complete and self.generation_algorithm == "prims_algorithm" and cell in self.frontier:
                    # Sınır hücreleri için daha açık kırmızı
                    pygame.draw.rect(screen, (153, 0, 0), (x, y, cell_size, cell_size))
                
                # Başlangıç ve bitiş noktalarını özel olarak göster
                if cell.is_start:
                    # Başlangıç hücresi için yeşil dikdörtgen
                    pygame.draw.rect(screen, (0, 255, 0), (x, y, cell_size, cell_size))
                    center_x = x + cell_size // 2
                    center_y = y + cell_size // 2
                    pygame.draw.circle(screen, (255, 0, 0), (center_x, center_y), cell_size // 4)
                elif cell.is_end:
                    # Bitiş hücresi için kırmızı dikdörtgen
                    pygame.draw.rect(screen, (255, 0, 0), (x, y, cell_size, cell_size))
                
                # Duvarları çiz (kırmızı renkte)
                line_width = max(2, cell_size // 10)
                wall_color = (255, 0, 0)  # Duvarlar kırmızı
                if cell.walls["top"]:
                    pygame.draw.line(screen, wall_color, (x, y), (x + cell_size, y), line_width)
                if cell.walls["right"]:
                    pygame.draw.line(screen, wall_color, (x + cell_size, y), (x + cell_size, y + cell_size), line_width)
                if cell.walls["bottom"]:
                    pygame.draw.line(screen, wall_color, (x, y + cell_size), (x + cell_size, y + cell_size), line_width)
                if cell.walls["left"]:
                    pygame.draw.line(screen, wall_color, (x, y), (x, y + cell_size), line_width)
    
    def clear_solution(self):
        """Labirentteki çözüm yollarını ve işaretleri temizle."""
        for row in self.grid:
            for cell in row:
                # Hücre verilerini koruyarak sadece çözüm ile ilgili işaretleri temizle
                cell.visited = False
                cell.is_path = False
                cell.is_solution = False
                cell.distance = float('inf')
                cell.parent = None
        
        # Başlangıç ve bitiş noktalarını yeniden işaretle
        self.start_cell.is_start = True
        self.end_cell.is_end = True
    
    def clear_path_only(self):
        """Sadece geçici ziyaret izlerini temizle, çözüm yolunu koru."""
        for row in self.grid:
            for cell in row:
                # Ziyaret bayraklarını temizle ama çözüm yolunu koru
                if not cell.is_solution:
                    cell.visited = False
                    
        # Başlangıç ve bitiş noktalarını koruduğumuzdan emin olalım
        if self.start_cell:
            self.start_cell.is_start = True
        if self.end_cell:
            self.end_cell.is_end = True 