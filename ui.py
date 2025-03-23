import pygame
import time
from algorithms import *

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
# Yeni renk tanımlamaları
BACKGROUND_COLOR = BLACK  # Arka plan rengi
WALL_COLOR = RED  # Duvar rengi
VISITED_COLOR = (102, 0, 0)  # Ziyaret edilen hücre rengi (%40 opaklıkta kırmızı)
PANEL_COLOR = WHITE  # Sağ panel arka plan rengi (siyahtan beyaza değiştirdim)
BUTTON_COLOR = BLACK  # Buton arka plan rengi
TEXT_COLOR = RED  # Yazı rengi

class Button:
    def __init__(self, x, y, width, height, text, font, color=BUTTON_COLOR, hover_color=DARK_GRAY, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        # Eğer "Algoritmayı Sıfırla" veya "Çıkış" ise farklı renk kullan
        if text == "Algoritmayı Sıfırla" or text == "Çıkış":
            self.text_color = BLACK
        else:
            self.text_color = text_color
        self.hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, RED, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Dropdown:
    def __init__(self, x, y, width, height, options, font, label="", color=BUTTON_COLOR, hover_color=DARK_GRAY, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.selected_index = 0
        self.is_open = False
        self.label = label
        
        # Her seçenek için dikdörtgen oluştur - seçenekler hep aşağıda gösterilecek
        self.option_rects = []
        for i in range(len(options)):
            self.option_rects.append(pygame.Rect(x, y + (i+1) * height, width, height))
    
    def draw(self, screen):
        # Ana kutuyu çiz
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        pygame.draw.rect(screen, RED, self.rect, 2, border_radius=5)
        
        # Seçilen seçeneği göster
        text_surface = self.font.render(self.options[self.selected_index], True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Etiketi çiz
        if self.label:
            label_surface = self.font.render(self.label, True, self.text_color)
            label_rect = label_surface.get_rect(midright=(self.rect.left - 10, self.rect.centery))
            screen.blit(label_surface, label_rect)
        
        # Açık durumdaysa seçenekleri göster
        if self.is_open:
            for i, option_rect in enumerate(self.option_rects):
                color = self.hover_color if option_rect.collidepoint(pygame.mouse.get_pos()) else self.color
                pygame.draw.rect(screen, color, option_rect, border_radius=5)
                pygame.draw.rect(screen, RED, option_rect, 2, border_radius=5)
                
                option_text = self.font.render(self.options[i], True, self.text_color)
                option_text_rect = option_text.get_rect(center=option_rect.center)
                screen.blit(option_text, option_text_rect)
    
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return False
                
            if self.is_open:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.is_open = False
                        return True
                
                # Dropdown dışına tıklandıysa kapat
                self.is_open = False
        
        return False
    
    def get_selected(self):
        return self.options[self.selected_index]

class Slider:
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, font, label_text=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.dragging = False
        self.handle_rect = pygame.Rect(0, 0, 10, height + 4)
        self.set_handle_position()
        self.font = font
        self.label_text = label_text
        self.small_font = pygame.font.SysFont('Arial', 16)  # Daha küçük font
        
    def set_handle_position(self):
        """Slider tutacağının konumunu değere göre ayarla"""
        normalized = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.x + normalized * (self.width - self.handle_rect.width)
        self.handle_rect.x = handle_x
        self.handle_rect.y = self.rect.y - 2  # Biraz yukarıda konumlandır
    
    def handle_event(self, event):
        """Fare olaylarını işle ve değeri güncelle"""
        changed = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                changed = True  # İlk tıklama için değişim sinyali ver
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x = event.pos[0]
            # Tutacağın hareket sınırlarını kontrol et
            if mouse_x < self.rect.x:
                handle_x = self.rect.x
            elif mouse_x > self.rect.x + self.width - self.handle_rect.width:
                handle_x = self.rect.x + self.width - self.handle_rect.width
            else:
                handle_x = mouse_x
                
            # Tutacağı güncelle
            self.handle_rect.x = handle_x
            
            # Değeri güncelle
            normalized = (handle_x - self.rect.x) / (self.width - self.handle_rect.width)
            self.value = int(self.min_value + normalized * (self.max_value - self.min_value))
            
            changed = True
        
        return changed
    
    def draw(self, screen):
        """Slider'ı ekrana çiz"""
        # Çubuğu çiz
        pygame.draw.rect(screen, (150, 150, 150), self.rect)
        
        # Tutacağı çiz
        pygame.draw.rect(screen, (100, 100, 100), self.handle_rect)
        pygame.draw.rect(screen, RED, self.handle_rect, 1)  # Kenarlık kırmızı
        
        # Değeri göster
        value_text = self.small_font.render(f"{self.value}", True, TEXT_COLOR)
        value_rect = value_text.get_rect(center=(self.handle_rect.centerx, self.rect.y - 15))
        screen.blit(value_text, value_rect)
        
        # Etiket varsa göster
        if self.label_text:
            # Yazı rengini kırmızı yap
            label_text = self.small_font.render(self.label_text, True, TEXT_COLOR)
            # Etiketi daha yukarıda bir konuma yerleştir
            label_rect = label_text.get_rect(midtop=(self.rect.centerx, self.rect.y - 38))
            screen.blit(label_text, label_rect)

class UI:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Algoritma seçenekleri
        self.generation_algorithms = ["recursive_backtracking", "prims_algorithm"]
        self.generation_algorithm_names = {
            "recursive_backtracking": "Recursive Backtracking",
            "prims_algorithm": "Prim's Algorithm"
        }
        
        # Türkçe isimleri koruyalım
        self.generation_algorithm_names_tr = {
            "recursive_backtracking": "Geriye İzleme",
            "prims_algorithm": "Prim Algoritması"
        }
        
        self.solving_algorithms = ["wall_follower", "dijkstra", "dead_end_filling", "bfs", "dfs", "ids", "a_star"]
        self.solving_algorithm_names = {
            "wall_follower": "Wall Follower",
            "dijkstra": "Dijkstra",
            "dead_end_filling": "Dead End Filling",
            "bfs": "Breadth First Search",
            "dfs": "Depth First Search",
            "ids": "Iterative Deepening Search",
            "a_star": "A* Algorithm"
        }
        
        # Türkçe isimleri koruyalım
        self.solving_algorithm_names_tr = {
            "wall_follower": "Duvar Takip",
            "dijkstra": "Dijkstra",
            "dead_end_filling": "Çıkmaz Doldurma",
            "bfs": "Genişlik Öncelikli Arama",
            "dfs": "Derinlik Öncelikli Arama",
            "ids": "Yinelemeli Derinleştirme",
            "a_star": "A* Algoritması"
        }
        
        self.maze_size = 20  # Varsayılan labirent boyutu
        self.selected_algorithm = None
        
        # Panel pozisyonu ve boyutu
        self.panel_width = 300
        self.panel_x = self.width - self.panel_width
        
        # Menü öğelerini oluştur
        self.init_menu_elements()
    
    def init_menu_elements(self):
        button_width = 230
        button_height = 35
        margin = 10
        
        # Sağ panel butonları
        self.algorithm_buttons = []
        
        # Labirent boyutu ayarı - başlıktan daha aşağıda
        small_font = pygame.font.SysFont('Arial', 16)
        self.maze_size_slider = Slider(
            self.panel_x + self.panel_width // 2 - button_width // 2,
            80,  # 50'den 80'e çıkardım
            button_width, 10,
            5, 50, self.maze_size,
            small_font,
            "Maze Size"  # Labirent Boyutu -> Maze Size
        )
        
        # Labirent oluşturma algoritması seçimi - daha aşağı kaydır
        gen_algo_names = [self.generation_algorithm_names[algo] for algo in self.generation_algorithms]
        self.generation_algorithm_dropdown = Dropdown(
            self.panel_x + self.panel_width // 2 - button_width // 2,
            130,  # 100'den 130'a çıkardım
            button_width, button_height,
            gen_algo_names,
            self.small_font
        )
        
        # Labirent oluştur butonu - üsttekilere göre daha aşağıda
        self.generate_maze_button = Button(
            self.panel_x + self.panel_width // 2 - button_width // 2,
            230,  # 225'ten 230'a çıkardım (yarım punto daha aşağı)
            button_width, button_height,
            "Generate Maze",  # Labirent Oluştur -> Generate Maze
            self.font
        )
        
        # Algoritma seçimi bölümü - başlığı daha aşağıya alıyoruz
        y_pos = 330  # 290'dan 330'a çıkardım
        for i, algo in enumerate(self.solving_algorithms):
            algo_button = Button(
                self.panel_x + self.panel_width // 2 - button_width // 2,
                y_pos,
                button_width, button_height,
                self.solving_algorithm_names[algo],
                self.small_font
            )
            self.algorithm_buttons.append(algo_button)
            y_pos += button_height + margin
        
        # Algoritma sıfırla butonu - bir punto yukarı taşı
        self.reset_algorithm_button = Button(
            self.panel_x + self.panel_width // 2 - button_width // 2,
            y_pos + 5,  # 20'den 5'e düşürdüm (bir punto yukarı)
            button_width, button_height,
            "Reset Algorithm",  # Reset & Stop Algorithm -> Reset Algorithm
            self.font,
            color=(255, 200, 200),
            hover_color=(255, 150, 150)
        )
        
        # Türkçe çevirisi korumak için
        self.reset_algorithm_button_tr_text = "Algoritmayı Sıfırla"
        
        # Karşılaştır butonu - bir punto yukarı taşı
        self.compare_button = Button(
            self.panel_x + self.panel_width // 2 - button_width // 2,
            y_pos + 5 + button_height + margin,  # 20'den 5'e düşürdüm (bir punto yukarı)
            button_width, button_height,
            "Compare Algorithms",  # Algoritmaları Karşılaştır -> Compare Algorithms
            self.small_font
        )
        
        # Çıkış butonu
        self.quit_button = Button(
            self.panel_x + self.panel_width // 2 - button_width // 2,
            self.height - 60,
            button_width, button_height,
            "Exit",  # Çıkış -> Exit
            self.font,
            color=(255, 100, 100),
            hover_color=(255, 50, 50)
        )
        
        # Algoritma seçim kutucukları (karşılaştırma için)
        self.algorithm_checkboxes = []
        checkbox_size = 20
        checkbox_margin = 40
        checkbox_start_y = 120  # Daha yukarıda başlamak için 230'dan 120'ye değiştirdim
        
        for i, algo in enumerate(self.solving_algorithms):
            self.algorithm_checkboxes.append({
                "rect": pygame.Rect(self.width // 2 - 150, checkbox_start_y + i * checkbox_margin, checkbox_size, checkbox_size),
                "selected": False,
                "name": algo
            })
        
        # Geri dön butonu
        self.back_button = Button(
            50, self.height - 70,
            150, 50,
            "Back to Main",  # Ana Ekrana Dön -> Back to Main
            self.font
        )
    
    def draw_main_screen(self, maze=None):
        """Ana ekranı çiz (labirent ve sağ panel)"""
        # Arka planı siyah yap
        self.screen.fill(BACKGROUND_COLOR)
        
        # Sağ paneli çiz - artık siyah olacak
        pygame.draw.rect(self.screen, PANEL_COLOR, (self.panel_x, 0, self.panel_width, self.height))
        pygame.draw.line(self.screen, RED, (self.panel_x, 0), (self.panel_x, self.height), 2)
        
        # Panel başlığı - yazı rengi kırmızı olacak
        title_font = pygame.font.SysFont('Arial', 28, bold=True)
        title = title_font.render("Maze Solver", True, TEXT_COLOR)  # Labirent Çözücü -> Maze Solver
        title_rect = title.get_rect(center=(self.panel_x + self.panel_width // 2, 25))
        self.screen.blit(title, title_rect)
        
        # Labirent boyutu ayarı
        self.maze_size_slider.draw(self.screen)
        
        # Oluşturma algoritması seçimi açıklaması - yazı rengi kırmızı olacak
        label_font = pygame.font.SysFont('Arial', 20)
        gen_label = label_font.render("Generation Algorithm:", True, TEXT_COLOR)  # Oluşturma Algoritması -> Generation Algorithm
        gen_label_rect = gen_label.get_rect(center=(self.panel_x + self.panel_width // 2, 115))  # 85'den 115'e çıkardım
        self.screen.blit(gen_label, gen_label_rect)
        
        # Dropdown'u çiz
        self.generation_algorithm_dropdown.draw(self.screen)
        
        # Labirent oluştur butonu
        self.generate_maze_button.draw(self.screen)
        
        # Algoritma seçimi bölümü - başlığı daha aşağıya alıyoruz
        pygame.draw.line(self.screen, RED, (self.panel_x + 10, 280), (self.panel_x + self.panel_width - 10, 280), 1)  # 260'dan 280'e çıkardım
        algo_title = label_font.render("Solving Algorithms", True, TEXT_COLOR)  # Çözme Algoritmaları -> Solving Algorithms
        algo_title_rect = algo_title.get_rect(center=(self.panel_x + self.panel_width // 2, 295))  # 275'den 295'e çıkardım
        self.screen.blit(algo_title, algo_title_rect)
        
        # Algoritma butonları
        for button in self.algorithm_buttons:
            button.draw(self.screen)
        
        # Algoritma sıfırla butonu
        self.reset_algorithm_button.draw(self.screen)
        
        # Karşılaştır butonu
        self.compare_button.draw(self.screen)
        
        # Çıkış butonu
        self.quit_button.draw(self.screen)
        
        # Eğer labirent varsa çiz
        if maze:
            self.draw_maze(maze)
    
    def draw_maze(self, maze):
        """Labirenti çiz"""
        # Labirent çizim boyutlarını hesapla (sağ paneli hesaba katarak)
        maze_area_width = self.width - self.panel_width
        maze_size = min(maze_area_width, self.height) - 80
        cell_size = maze_size // max(maze.rows, maze.cols)
        
        # Labirenti ortala
        offset_x = (maze_area_width - cell_size * maze.cols) // 2
        offset_y = (self.height - cell_size * maze.rows) // 2
        
        # Labirenti çiz
        maze.draw(self.screen, cell_size, offset_x, offset_y)
    
    def draw_generation_info(self, maze):
        """Labirent oluşturma bilgilerini göster"""
        if not maze:
            return
            
        info_font = pygame.font.SysFont('Arial', 20)
        
        # Kullanılan algoritmanın adını al
        algorithm_name = "Recursive Backtracking" if maze.generation_algorithm == "recursive_backtracking" else "Prim's Algorithm"
        
        info_text = f"Algorithm: {algorithm_name} | Size: {maze.rows}x{maze.cols}"  # Algoritma -> Algorithm, Boyut -> Size
        
        info_surface = info_font.render(info_text, True, TEXT_COLOR)
        info_rect = info_surface.get_rect(center=((self.width - self.panel_width) // 2, 30))
        self.screen.blit(info_surface, info_rect)
    
    def draw_solving_info(self, algorithm):
        """Algoritma çözüm bilgilerini göster"""
        if not algorithm:
            return
            
        info_font = pygame.font.SysFont('Arial', 20)
        
        elapsed_time = algorithm.elapsed_time if hasattr(algorithm, "elapsed_time") else 0
        visited_cells = algorithm.visited_count if hasattr(algorithm, "visited_count") else 0
        path_length = algorithm.path_length if hasattr(algorithm, "path_length") else 0
        
        info_text = f"Algorithm: {algorithm.name} | Time: {elapsed_time:.3f}s | Visited: {visited_cells} | Path: {path_length}"  # Algoritma -> Algorithm, Süre -> Time, Ziyaret -> Visited, Yol -> Path
        
        info_surface = info_font.render(info_text, True, TEXT_COLOR)
        info_rect = info_surface.get_rect(center=((self.width - self.panel_width) // 2, 30))
        self.screen.blit(info_surface, info_rect)
        
        # Seçili algoritmayı vurgula - mevcut seçili algoritmayı kontrol et
        for i, algo_name in enumerate(self.solving_algorithms):
            button = self.algorithm_buttons[i]
            # Seçili algoritma adıyla doğrudan karşılaştır
            if algo_name == self.selected_algorithm:
                pygame.draw.rect(self.screen, GREEN, button.rect, 3, border_radius=5)
    
    def draw_comparison_screen(self, maze, algorithms):
        """Karşılaştırma ekranını çiz"""
        # Arka planı siyah yap
        self.screen.fill(BACKGROUND_COLOR)
        
        # Başlık - sola hizalı yap ve puntosunu düşür
        title_font = pygame.font.SysFont('Arial', 22, bold=True)
        title = title_font.render("Algorithm Comparison", True, WHITE)  # Algoritma Karşılaştırması -> Algorithm Comparison
        title_rect = title.get_rect(midleft=(30, 30))
        self.screen.blit(title, title_rect)
        
        n_algos = len(algorithms)
        if n_algos < 2 or n_algos > 4:
            return
        
        # Labirentleri çiz
        if n_algos == 2:
            # 1x2 grid
            rows, cols = 1, 2
        else:
            # 2x2 grid (3 veya 4 algoritma için)
            rows, cols = 2, 2
        
        # Tam ekran boyutunu kullan
        maze_width = (self.width - 60) // cols
        maze_height = (self.height - 200) // rows
        maze_size = min(maze_width // maze.cols, maze_height // maze.rows)
        
        # Labirentler için başlangıç noktası (merkezde olacak şekilde)
        start_x = (self.width - (cols * (maze.cols * maze_size + 20))) // 2
        start_y = 80
        
        algos_drawn = 0
        
        # Her bir labirenti ayrı ayrı çiz
        for r in range(rows):
            for c in range(cols):
                if algos_drawn >= n_algos:
                    break
                    
                algorithm = algorithms[algos_drawn]
                
                # Labirent pozisyonu
                maze_x = start_x + c * (maze.cols * maze_size + 40)
                maze_y = start_y + r * (maze.rows * maze_size + 100)
                
                # Algoritma adını göster - puntosunu düşür
                algo_font = pygame.font.SysFont('Arial', 16)
                algo_surface = algo_font.render(algorithm.name, True, WHITE)
                algo_rect = algo_surface.get_rect(center=(maze_x + (maze.cols * maze_size) // 2, maze_y - 30))
                self.screen.blit(algo_surface, algo_rect)
                
                # Her algoritma için bilgileri göster - puntosunu düşür
                info_font = pygame.font.SysFont('Arial', 12)
                
                elapsed_time = algorithm.elapsed_time if hasattr(algorithm, "elapsed_time") else 0
                visited_cells = algorithm.visited_count if hasattr(algorithm, "visited_count") else 0
                path_length = algorithm.path_length if hasattr(algorithm, "path_length") else 0
                
                time_surface = info_font.render(f"Time: {elapsed_time:.3f}s", True, WHITE)  # Süre -> Time
                visited_surface = info_font.render(f"Visited: {visited_cells}", True, WHITE)  # Ziyaret -> Visited
                path_surface = info_font.render(f"Path: {path_length}", True, WHITE)  # Yol -> Path
                
                self.screen.blit(time_surface, (maze_x, maze_y - 60))
                self.screen.blit(visited_surface, (maze_x + maze.cols * maze_size - 100, maze_y - 60))
                self.screen.blit(path_surface, (maze_x + maze.cols * maze_size // 2 - 40, maze_y - 60))
                
                # Labirenti çiz - önemli: HER ALGORİTMA KENDİ ÇÖZÜMÜNÜ GÖSTERMELİ
                for row in range(maze.rows):
                    for col in range(maze.cols):
                        cell = maze.grid[row][col]
                        cell_x = maze_x + col * maze_size
                        cell_y = maze_y + row * maze_size
                        
                        # Arka plan rengini belirle
                        color = (0, 0, 0)  # Arka plan siyah
                        
                        # İlgili algoritmanın visited/path/solution değerlerine göre renk belirle
                        if hasattr(algorithm, 'visited_cells') and cell in algorithm.visited_cells:
                            color = (102, 0, 0)  # Ziyaret edilmiş hücre için koyu kırmızı
                        
                        # ÖNEMLİ DEĞİŞİKLİK: Her algoritma kendi çözüm yolunu göstermeli
                        # Bu hücre algoritmanın çözüm yolunda mı kontrol et
                        if hasattr(algorithm, 'solution_found') and algorithm.solution_found:
                            # Başlangıç hücresinden hedef hücreye parent ilişkisini izle
                            current = maze.end_cell
                            solution_path = [current]
                            
                            # Parent ilişkisini izleyerek çözüm yolunu oluştur
                            while current and current != maze.start_cell:
                                current = current.parent
                                if current:
                                    solution_path.append(current)
                            
                            # Bu hücre çözüm yolunda mı kontrol et
                            if cell in solution_path:
                                color = (255, 255, 0)  # Sarı - çözüm yolu
                        
                        # Başlangıç ve bitiş noktaları için renk kontrolü
                        if cell.is_start:
                            color = (0, 255, 0)  # Başlangıç hücresi için yeşil
                        elif cell.is_end:
                            color = (255, 0, 0)  # Bitiş hücresi için kırmızı
                        
                        # Hücre arka planını çiz
                        pygame.draw.rect(self.screen, color, (cell_x, cell_y, maze_size, maze_size))
                        
                        # Başlangıç ve bitiş noktalarını özel olarak göster
                        if cell.is_start:
                            center_x = cell_x + maze_size // 2
                            center_y = cell_y + maze_size // 2
                            pygame.draw.circle(self.screen, (255, 0, 0), (center_x, center_y), maze_size // 4)
                        
                        # Duvarları çiz
                        line_width = max(1, maze_size // 10)
                        wall_color = (255, 0, 0)  # Duvarlar kırmızı
                        if cell.walls["top"]:
                            pygame.draw.line(self.screen, wall_color, 
                                            (cell_x, cell_y), 
                                            (cell_x + maze_size, cell_y), line_width)
                        if cell.walls["right"]:
                            pygame.draw.line(self.screen, wall_color, 
                                            (cell_x + maze_size, cell_y), 
                                            (cell_x + maze_size, cell_y + maze_size), line_width)
                        if cell.walls["bottom"]:
                            pygame.draw.line(self.screen, wall_color, 
                                            (cell_x, cell_y + maze_size), 
                                            (cell_x + maze_size, cell_y + maze_size), line_width)
                        if cell.walls["left"]:
                            pygame.draw.line(self.screen, wall_color, 
                                            (cell_x, cell_y), 
                                            (cell_x, cell_y + maze_size), line_width)
                
                algos_drawn += 1
        
        # Sonuçları göster - sağa hizalı yap ve puntosunu düşür
        if all(hasattr(a, "elapsed_time") and a.is_finished() for a in algorithms):
            # En hızlı algoritmayı bul
            fastest = min(algorithms, key=lambda a: a.elapsed_time if hasattr(a, "elapsed_time") else float('inf'))
            
            # En az hücre ziyaret edeni bul
            most_efficient = min(algorithms, key=lambda a: a.visited_count if hasattr(a, "visited_count") else float('inf'))
            
            # En kısa yol bulanı bul (path_length)
            shortest_path = min([a for a in algorithms if hasattr(a, "path_length") and a.path_length > 0], 
                               key=lambda a: a.path_length, default=None)
            
            # Sonuçları göster - sağa hizala ve puntoyu düşür
            result_font = pygame.font.SysFont('Arial', 18, bold=True)
            
            result_text = f"Fastest: {fastest.name} ({fastest.elapsed_time:.3f}s)"  # En Hızlı -> Fastest
            fastest_surface = result_font.render(result_text, True, GREEN)
            fastest_rect = fastest_surface.get_rect(bottomright=(self.width - 30, self.height - 100))
            self.screen.blit(fastest_surface, fastest_rect)
            
            # "En Verimli" yazısını SARI yap
            result_text = f"Most Efficient: {most_efficient.name} ({most_efficient.visited_count} visits)"  # En Verimli -> Most Efficient, ziyaret -> visits
            efficient_surface = result_font.render(result_text, True, YELLOW)  # Mavi yerine sarı
            efficient_rect = efficient_surface.get_rect(bottomright=(self.width - 30, self.height - 60))
            self.screen.blit(efficient_surface, efficient_rect)
        
        # Geri butonu
        self.back_button.draw(self.screen)
    
    def draw_comparison_selection(self):
        """Karşılaştırma seçim ekranını çiz"""
        # Arka planı siyah yap
        self.screen.fill(BACKGROUND_COLOR)
        
        # Başlık - puntosunu düşür
        title_font = pygame.font.SysFont('Arial', 28, bold=True)  # 36'dan 28'e düşürdüm
        title = title_font.render("Select Algorithms to Compare", True, WHITE)  # Karşılaştırılacak Algoritmaları Seçin -> Select Algorithms to Compare
        title_rect = title.get_rect(center=(self.width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Algoritma seçim kutucuklarını çiz
        for i, checkbox in enumerate(self.algorithm_checkboxes):
            # Checkbox'ı çiz
            pygame.draw.rect(self.screen, WHITE, checkbox["rect"], 2)
            if checkbox["selected"]:
                # Seçiliyse içini doldur
                pygame.draw.rect(self.screen, GREEN, pygame.Rect(checkbox["rect"].x + 3, checkbox["rect"].y + 3, 
                                                                checkbox["rect"].width - 6, checkbox["rect"].height - 6))
            
            # Algoritma adını çiz - puntosunu düşür
            algo_name = self.solving_algorithm_names[checkbox["name"]]
            text = pygame.font.SysFont('Arial', 18).render(algo_name, True, WHITE)  # Özel font kullanarak 24'ten 18'e düşür
            self.screen.blit(text, (checkbox["rect"].x + 30, checkbox["rect"].y))
        
        # Başlat butonu - yazı rengini siyah yap ve puntosunu düşür
        start_compare_button = Button(
            self.width // 2 - 100, 
            self.height - 100,
            200, 50,
            "Start Comparison",  # Karşılaştırmayı Başlat -> Start Comparison
            pygame.font.SysFont('Arial', 16),  # 20'den 16'ya düşürdüm
            color=GREEN,
            hover_color=(0, 200, 0),
            text_color=BLACK
        )
        start_compare_button.draw(self.screen)
        
        # Geri butonu
        self.back_button.draw(self.screen)
        
        return start_compare_button
    
    def handle_main_screen_events(self, event, maze=None):
        """Ana ekran olaylarını işle"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Labirent boyutu ayarı
        if self.maze_size_slider.handle_event(event):
            return "maze_size_changed"
        
        # Oluşturma algoritması seçimi
        if self.generation_algorithm_dropdown.handle_event(event):
            return "generation_algorithm_changed"
        
        # Butonların üzerinde olma durumunu güncelle
        self.generate_maze_button.is_hover(mouse_pos)
        self.reset_algorithm_button.is_hover(mouse_pos)
        self.compare_button.is_hover(mouse_pos)
        self.quit_button.is_hover(mouse_pos)
        
        for button in self.algorithm_buttons:
            button.is_hover(mouse_pos)
        
        # Buton tıklama olaylarını kontrol et
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.generate_maze_button.is_clicked(mouse_pos, event):
                return "generate_maze"
            elif self.reset_algorithm_button.is_clicked(mouse_pos, event):
                return "reset_algorithm"
            elif self.compare_button.is_clicked(mouse_pos, event):
                return "show_comparison_selection"
            elif self.quit_button.is_clicked(mouse_pos, event):
                return "quit"
            
            # Algoritma butonlarını kontrol et
            for i, button in enumerate(self.algorithm_buttons):
                if button.is_clicked(mouse_pos, event):
                    self.selected_algorithm = self.solving_algorithms[i]
                    return "select_algorithm"
        
        return None
    
    def handle_comparison_selection_events(self, event, start_compare_button):
        """Karşılaştırma seçim ekranı olaylarını işle"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Butonların üzerinde olma durumunu güncelle - start_compare_button None değilse kontrol et
        if start_compare_button:
            start_compare_button.is_hover(mouse_pos)
        self.back_button.is_hover(mouse_pos)
        
        # Buton tıklama olaylarını kontrol et
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Algoritma kutucuklarını kontrol et
            for checkbox in self.algorithm_checkboxes:
                if checkbox["rect"].collidepoint(mouse_pos):
                    # Eğer zaten seçiliyse, seçimi kaldır
                    if checkbox["selected"]:
                        checkbox["selected"] = False
                    else:
                        # Eğer seçili değilse, şu andaki seçili sayısını kontrol et
                        selected_count = sum(1 for cb in self.algorithm_checkboxes if cb["selected"])
                        # Eğer 4'ten az seçiliyse, yeni seçime izin ver
                        if selected_count < 4:
                            checkbox["selected"] = True
                        # Aksi takdirde, kullanıcıya bir uyarı mesajı göster
                        else:
                            print("En fazla 4 algoritma seçebilirsiniz!")
                    return None
            
            # Karşılaştırmayı başlat butonunu kontrol et
            if start_compare_button and start_compare_button.is_clicked(mouse_pos, event):
                # En az 2, en fazla 4 algoritma seçildiğinden emin ol
                selected_count = sum(1 for cb in self.algorithm_checkboxes if cb["selected"])
                if 2 <= selected_count <= 4:
                    return "start_comparison"
                elif selected_count < 2:
                    print("En az 2 algoritma seçmelisiniz!")
                    return None
            
            # Geri butonunu kontrol et
            if self.back_button.is_clicked(mouse_pos, event):
                return "back_to_main"
        
        return None
    
    def get_maze_size(self):
        return self.maze_size_slider.value
    
    def get_generation_algorithm(self):
        selected_name = self.generation_algorithm_dropdown.get_selected()
        # Türkçe isimden algoritma koduna dönüştür
        for algo, name in self.generation_algorithm_names.items():
            if name == selected_name:
                return algo
        # Bulunamazsa varsayılan algoritma
        return self.generation_algorithms[0]
    
    def get_selected_algorithm(self, maze=None):
        """Seçilen algoritmayı döndür"""
        if not self.selected_algorithm:
            return None
            
        # Eğer maze parametresi verilmişse, algoritmayı oluştur
        if maze:
            return create_algorithm(self.selected_algorithm, maze)
        else:
            # Aksi halde sadece adını içeren bir nesne döndür
            # Bu obje sadece görüntüleme amaçlı kullanılmalı, adım yürütmek için değil
            dummy_algo = type('DummyAlgo', (), {
                'name': self.solving_algorithm_names[self.selected_algorithm], 
                'step': lambda: None, 
                'is_finished': False  # Şimdi bu bir özellik
            })
            return dummy_algo()
    
    def get_comparison_algorithms(self):
        """Karşılaştırma için seçilen algoritmaların adlarını döndür"""
        selected_algos = []
        for checkbox in self.algorithm_checkboxes:
            if checkbox["selected"]:
                selected_algos.append(checkbox["name"])
        
        return selected_algos
    
    def handle_comparison_events(self, event):
        """Karşılaştırma ekranı olaylarını işle (sadece geri butonu için)"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Geri butonunun üzerinde olma durumunu güncelle
        self.back_button.is_hover(mouse_pos)
        
        # Buton tıklama olaylarını kontrol et
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Geri butonunu kontrol et
            if self.back_button.is_clicked(mouse_pos, event):
                return "back_to_main"
        
        return None 