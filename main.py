import pygame
import sys
from maze import Maze
from algorithms import *
from ui import UI

# Pygame başlangıç ayarları
pygame.init()
pygame.font.init()
width, height = 1200, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Maze Solver Visualizer")
clock = pygame.time.Clock()

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

class MazeSolver:
    def __init__(self):
        self.ui = UI(screen, width, height)
        self.maze = None
        self.screen = screen
        self.running = True
        self.state = "main"  # main, solving, comparison, comparison_selection, generating_maze
        self.current_algorithm = None
        self.comparison_algorithms = []
        self.paused = False  # Duraklatma durumu
        self._after_generation = None  # Labirent oluşturma sonrası yapılacak işlem
        self.solution_message_shown = False  # Çözüm mesajının gösterilip gösterilmediğini kontrol eden bayrak
        
    def run(self):
        while self.running:
            # Olayları işle
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Mevcut duruma göre işlem yap
            if self.state == "main":
                self.handle_main_screen(events)
            elif self.state == "solving":
                self.handle_solving(events)
            elif self.state == "comparison":
                self.handle_comparison(events)
            elif self.state == "comparison_selection":
                self.handle_comparison_selection(events)
            elif self.state == "generating_maze":
                self.handle_generating_maze(events)
                
            pygame.display.flip()
            clock.tick(60)
    
    def handle_main_screen(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            # Ana ekran olaylarını işle
            action = self.ui.handle_main_screen_events(event, self.maze)
            if action:
                if action == "generate_maze":
                    # Yeni labirent oluşturulacak
                    # Labirenti değiştirmeden önce, mevcut algoritma adını saklayalım
                    previous_algo = self.ui.selected_algorithm
                    
                    # Yeni labirent oluştur
                    size = self.ui.get_maze_size()
                    algorithm = self.ui.get_generation_algorithm()
                    self.maze = Maze(size, size)
                    self.maze.set_generation_algorithm(algorithm)
                    
                    # Çalışan algoritmayı temizle ama UI'daki seçimi koru
                    self.current_algorithm = None
                    
                    # Labirent oluşturma durumuna geç
                    self.state = "generating_maze"
                    
                    # Mesaj bayrağını sıfırla
                    self.solution_message_shown = False
                    
                elif action == "select_algorithm":
                    if self.maze is None:
                        # Önce bir labirent oluştur
                        size = self.ui.get_maze_size()
                        algorithm = self.ui.get_generation_algorithm()
                        self.maze = Maze(size, size)
                        self.maze.set_generation_algorithm(algorithm)
                        
                        # Labirent oluşturma durumuna geç
                        self.state = "generating_maze"
                    else:
                        # Eğer labirent zaten varsa ve önceki bir algoritma çalıştıysa, çizimleri temizle
                        self.maze.clear_solution()
                    
                        # Algoritmayı seç ve başlat
                        self.current_algorithm = self.ui.get_selected_algorithm(self.maze)
                        if self.current_algorithm:
                            self.current_algorithm.initialize()
                            self.state = "solving"  # Çözme durumuna geç
                    
                elif action == "reset_algorithm":
                    # Mevcut algoritmayı sıfırla
                    if self.maze:
                        self.maze.clear_solution()
                        
                        # Eğer seçili bir algoritma varsa, sıfırla
                        if self.ui.selected_algorithm:
                            self.current_algorithm = self.ui.get_selected_algorithm(self.maze)
                            if self.current_algorithm:
                                self.current_algorithm.initialize()
                                self.state = "solving"  # Çözme durumuna geç
                                # Mesaj bayrağını sıfırla
                                self.solution_message_shown = False
                                return
                        
                        # Algoritma seçili değilse ana ekrana dön
                        self.current_algorithm = None
                        self.state = "main"
                        # Mesaj bayrağını sıfırla
                        self.solution_message_shown = False
                    
                elif action == "show_comparison_selection":
                    if self.maze:  # Labirent oluşturulmuşsa
                        self.state = "comparison_selection"
                    
                elif action == "quit":
                    print("Çıkış yapılıyor...")
                    self.running = False
                    pygame.quit()
                    sys.exit()
                    
                elif action == "maze_size_changed":
                    # Kullanıcı labirent boyutunu değiştirdi, bir şey yapmaya gerek yok
                    pass
                    
                elif action == "generation_algorithm_changed":
                    # Kullanıcı oluşturma algoritmasını değiştirdi, bir şey yapmaya gerek yok
                    pass
        
        # Ana ekranı çiz
        self.ui.draw_main_screen(self.maze)
        
        # Eğer algoritma çalışıyorsa bilgileri göster
        if self.current_algorithm:
            self.ui.draw_solving_info(self.current_algorithm)
    
    def handle_generating_maze(self, events):
        """Labirent oluşturma durumunu işle"""
        # ESC tuşuyla ana ekrana dönebilme
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"
                    self._after_generation = None
                if event.key == pygame.K_SPACE:
                    # Hızlı tamamlama - tüm adımları tamamla
                    while not self.maze.generation_complete:
                        self.maze.generate_step()

        # Labirent oluşturma adımını yap
        is_complete = self.maze.generate_step()
        
        # Ana ekranı çiz
        self.ui.draw_main_screen(self.maze)
        self.ui.draw_generation_info(self.maze)
        
        # Durum mesajını göster
        font = pygame.font.SysFont('Arial', 24)
        text = font.render("Labirent Oluşturuluyor... (ESC: İptal, SPACE: Hızlı Tamamla)", True, RED)
        text_rect = text.get_rect(center=((self.screen.get_width() - self.ui.panel_width) // 2, self.screen.get_height() - 30))
        self.screen.blit(text, text_rect)
        
        # Labirent tamamlandıysa
        if is_complete:
            # Oluşturma sonrası ne yapılacak?
            if self._after_generation == "comparison":
                # Karşılaştırma için algoritmaları başlat
                self.maze.clear_solution()
                self.start_comparison()
                self._after_generation = None
            else:
                # Labirent oluşturuldu, ana ekrana dön
                # Önceki algoritma seçimini temizle
                self.current_algorithm = None
                # Ana ekrana dön, kullanıcı yeniden algoritma seçebilir
                self.state = "main"
                self._after_generation = None
    
    def handle_solving(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"
                    if self.maze:
                        self.maze.clear_solution()
                    # Algoritma değişince mesaj bayrağını sıfırla
                    self.solution_message_shown = False
                if event.key == pygame.K_SPACE:
                    # Çözüm algoritmasını başlat/duraklat
                    self.paused = not self.paused
                    
            # Ana ekran olaylarını işle
            action = self.ui.handle_main_screen_events(event, self.maze)
            if action:
                if action == "generate_maze":
                    # Yeni labirent oluşturulacak
                    # Labirenti değiştirmeden önce, mevcut algoritma adını saklayalım
                    previous_algo = self.ui.selected_algorithm
                    
                    # Yeni labirent oluştur
                    size = self.ui.get_maze_size()
                    algorithm = self.ui.get_generation_algorithm()
                    self.maze = Maze(size, size)
                    self.maze.set_generation_algorithm(algorithm)
                    
                    # Çalışan algoritmayı temizle ama UI'daki seçimi koru
                    self.current_algorithm = None
                    
                    # Labirent oluşturma durumuna geç
                    self.state = "generating_maze"
                    
                    # Mesaj bayrağını sıfırla
                    self.solution_message_shown = False
                
                elif action == "select_algorithm":
                    # Labirent yoksa oluştur
                    if self.maze is None:
                        size = self.ui.get_maze_size()
                        algorithm = self.ui.get_generation_algorithm()
                        self.maze = Maze(size, size)
                        self.maze.set_generation_algorithm(algorithm)
                        
                        # Labirent oluşturma durumuna geç
                        self.state = "generating_maze"
                    else:
                        # Mevcut çözümü temizle
                        self.maze.clear_solution()
                    
                    # Yeni algoritma oluştur ve başlat (solving durumunda kalıyoruz)
                    self.current_algorithm = self.ui.get_selected_algorithm(self.maze)
                    if self.current_algorithm:
                        self.current_algorithm.initialize()
                        
                    # Mesaj bayrağını sıfırla
                    self.solution_message_shown = False
                
                elif action == "reset_algorithm":
                    # Mevcut algoritmayı sıfırla
                    if self.maze:
                        self.maze.clear_solution()
                        
                        # Eğer seçili bir algoritma varsa, sıfırla
                        if self.ui.selected_algorithm:
                            self.current_algorithm = self.ui.get_selected_algorithm(self.maze)
                            if self.current_algorithm:
                                self.current_algorithm.initialize()
                                self.state = "solving"  # Çözme durumuna geç
                                # Mesaj bayrağını sıfırla
                                self.solution_message_shown = False
                                return
                        
                        # Algoritma seçili değilse ana ekrana dön
                        self.current_algorithm = None
                        self.state = "main"
                        # Mesaj bayrağını sıfırla
                        self.solution_message_shown = False
                
                elif action == "show_comparison_selection":
                    if self.maze:
                        self.state = "comparison_selection"
                
                elif action == "quit":
                    self.running = False
                    pygame.quit()
                    sys.exit()
                
                elif action == "back_to_main" or action == "back":
                    self.state = "main"
                    if self.maze:
                        self.maze.clear_solution()
        
        # Algoritma çözümünü bir adım ilerlet (duraklatılmadıysa)
        if self.current_algorithm and not self.paused:
            try:
                finished = self.current_algorithm.step()
                # Algoritma tamamlandıysa çözüm durumunu kontrol et
                if finished:
                    if self.current_algorithm.solution_found:
                        # Çözüm bulunmuşsa, sadece ziyaret izlerini temizle, çözüm yolunu koru
                        if not self.solution_message_shown:  # Eğer mesaj daha önce gösterilmediyse
                            print(f"Çözüm bulundu! Süre: {self.current_algorithm.elapsed_time:.3f}s")
                            self.solution_message_shown = True  # Mesaj gösterildi olarak işaretle
                        self.maze.clear_path_only()  # Sadece ziyaret izlerini temizle, çözüm yolunu koru
                    else:
                        # Çözüm bulunamadıysa, bir mesaj göster
                        if not self.solution_message_shown:  # Eğer mesaj daha önce gösterilmediyse
                            print("Algoritma tamamlandı ancak çözüm bulunamadı.")
                            self.solution_message_shown = True  # Mesaj gösterildi olarak işaretle
            except Exception as e:
                print(f"Algoritma çalıştırılırken hata oluştu: {str(e)}")
                # Hata durumunda ana ekrana dön
                self.state = "main"
        
        # Ana ekranı çiz
        self.ui.draw_main_screen(self.maze)
        self.ui.draw_solving_info(self.current_algorithm)
        
        # Duraklatma durumunu göster
        if self.paused:
            font = pygame.font.SysFont('Arial', 36, bold=True)
            text = font.render("DURAKLATILDI", True, RED)
            text_rect = text.get_rect(center=((self.screen.get_width() - self.ui.panel_width) // 2, 70))
            self.screen.blit(text, text_rect)
    
    def handle_comparison_selection(self, events):
        start_compare_button = self.ui.draw_comparison_selection()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            # Karşılaştırma seçim olaylarını işle
            action = self.ui.handle_comparison_selection_events(event, start_compare_button)
            if action:
                if action == "start_comparison":
                    if self.maze is None:
                        # Önce bir labirent oluştur
                        size = self.ui.get_maze_size()
                        algorithm = self.ui.get_generation_algorithm()
                        self.maze = Maze(size, size)
                        self.maze.set_generation_algorithm(algorithm)
                        
                        # Labirent oluşturma durumuna geç, ama karşılaştırma flag'ini ayarla
                        self._after_generation = "comparison"
                        self.state = "generating_maze"
                    else:
                        # Mevcut labirenti temizle
                        self.maze.clear_solution()
                        
                        # Karşılaştırma algoritmalarını oluştur ve başlat
                        self.start_comparison()
                    
                elif action == "back_to_main":
                    self.state = "main"
    
    def start_comparison(self):
        """Karşılaştırma algoritmalarını oluştur ve başlat"""
        # Karşılaştırma algoritmalarını oluştur
        selected_algos = self.ui.get_comparison_algorithms()
        self.comparison_algorithms = []
        
        # Mevcut labirenti temizle ve kopyala
        # Orijinal maze'in yapısını karşılaştırma için koruyoruz
        if self.maze:
            self.maze.clear_solution()  # Önce çözüm izlerini temizle
            
            # Tüm seçilen algoritmalar için labirenti kullan
            for algo_name in selected_algos:
                # Her algoritma için aynı maze kopya kullanılır
                algorithm = create_algorithm(algo_name, self.maze)
                algorithm.initialize()
                self.comparison_algorithms.append(algorithm)
        
        # Yeterli algoritma seçimi yoksa uyarı ver
        if len(self.comparison_algorithms) < 2:
            print("Karşılaştırma için en az 2 algoritma seçmelisiniz!")
            return
        
        self.state = "comparison"
    
    def handle_comparison(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "main"
                    if self.maze:
                        self.maze.clear_solution()
                if event.key == pygame.K_SPACE:
                    # Karşılaştırmayı başlat/duraklat
                    self.paused = not self.paused
        
            # Geri butonunu kontrol et
            # Burada None değil, özel bir back_button geçiyoruz ve sadece back_to_main işlemini kontrol ediyoruz
            action = self.ui.handle_comparison_events(event)
            if action == "back_to_main":
                self.state = "main"
                if self.maze:
                    self.maze.clear_solution()
        
        # Tüm algoritmaları bir adım ilerlet
        all_finished = True
        if not self.paused:
            for algorithm in self.comparison_algorithms:
                if not algorithm.is_finished():
                    finished = algorithm.step()
                    if not finished:
                        all_finished = False
        
        # Karşılaştırmayı çiz
        self.ui.draw_comparison_screen(self.maze, self.comparison_algorithms)
        
        # Duraklatma durumunu göster
        if self.paused:
            font = pygame.font.SysFont('Arial', 36, bold=True)
            text = font.render("DURAKLATILDI", True, RED)
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 70))
            self.screen.blit(text, text_rect)

if __name__ == "__main__":
    app = MazeSolver()
    app.run()
    pygame.quit()
    sys.exit() 