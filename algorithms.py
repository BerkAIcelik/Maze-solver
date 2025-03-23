import time
import heapq
import random
from collections import deque

class MazeSolvingAlgorithm:
    """Temel labirent çözme algoritması sınıfı."""
    
    def __init__(self, maze):
        self.maze = maze
        self.start_cell = maze.start_cell
        self.end_cell = maze.end_cell
        self.current_cell = None
        self.visited_cells = set()
        self.path = []
        self.solution_found = False
        self._is_finished = False  # Özel değişken, is_finished() metodu tarafından kullanılacak
        self.visited_count = 0
        self.path_length = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.name = "Base Algorithm"
    
    def initialize(self):
        """Algoritmayı başlat."""
        # Tüm hücrelerin yol verilerini sıfırla
        for row in self.maze.grid:
            for cell in row:
                cell.reset_path_data()
        
        # Başlangıç ve bitiş hücrelerini al
        self.start_cell = self.maze.start_cell
        self.end_cell = self.maze.end_cell
        
        # Başlangıçı işaretle
        self.start_cell.is_start = True
        self.end_cell.is_end = True
        
        self.current_cell = self.start_cell
        self.visited_cells = set([self.start_cell])
        self.current_cell.visited = True
        self.path = [self.current_cell]
        self.solution_found = False
        self._is_finished = False
        self.visited_count = 1
        self.path_length = 0
        self.start_time = time.time()
        self.elapsed_time = 0
    
    def is_finished(self):
        """Algoritmanın tamamlanıp tamamlanmadığını kontrol et."""
        return self._is_finished
    
    def step(self):
        """Algoritmanın bir adımını gerçekleştir."""
        if self._is_finished:
            return True
        
        # Başlangıçta veya adım sonrasında hedef kontrolü
        if self.current_cell == self.end_cell:
            self.solution_found = True
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            self.reconstruct_path()
            return True
        
        return False
    
    def reconstruct_path(self):
        """Çözüm yolunu yeniden oluştur ve hücreleri işaretle."""
        if not self.solution_found:
            return
        
        # Çözüm yolunu işaretle (varsa ebeveyn zinciri ile)
        current = self.end_cell
        path = []
        
        while current and current != self.start_cell:
            path.append(current)
            current.is_solution = True
            current.is_path = True  # Çözüm yolundaki hücreler de path olarak işaretlenir
            current = current.parent
        
        # Başlangıç noktasını ekle
        if self.start_cell:
            self.start_cell.is_solution = True
            self.start_cell.is_path = True  # Başlangıç da path olarak işaretlenir
        
        # Yol uzunluğunu hesapla
        self.path_length = len(path)
    
    def mark_visited(self, cell):
        """Ziyaret edilen hücreyi işaretle."""
        if cell not in self.visited_cells:
            cell.visited = True
            # cell.is_path = True  # Bu satırı kaldırıyorum, böylece ziyaret edilen yerler sarı olmayacak
            self.visited_cells.add(cell)
            self.visited_count += 1

class WallFollower(MazeSolvingAlgorithm):
    """Duvar Takip Algoritması (Right-Hand Rule)."""
    
    def __init__(self, maze):
        super().__init__(maze)
        self.name = "Duvar Takip"
        self.facing = "right"  # Başlangıçta sağa doğru bakıyor
        self.directions = ["up", "right", "down", "left"]
        self.direction_to_wall = {
            "up": "top", "right": "right", "down": "bottom", "left": "left"
        }
        self.direction_to_offset = {
            "up": (-1, 0), "right": (0, 1), "down": (1, 0), "left": (0, -1)
        }
        self.path_cells = []  # Ziyaret edilen hücrelerin sırasını takip etmek için
    
    def initialize(self):
        super().initialize()
        self.facing = "right"  # Başlangıçta sağa doğru bakıyor
        self.path_cells = [self.start_cell]  # Ziyaret yolu başlangıç hücresiyle başlar
    
    def step(self):
        # Tamamlanma durumunu kontrol et
        if self._is_finished:
            return True
        
        # Başlangıçta hedef kontrolü
        if self.current_cell == self.end_cell:
            self.solution_found = True
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            # Özel path takibimizi kullanarak reconstruct_path'i çağıralım
            self.reconstruct_path_from_visited()
            print("WallFollower: Hedef noktaya ulaşıldı!")
            return True
        
        # Sağ el kuralını uygula
        direction_index = self.directions.index(self.facing)
        test_order = [
            (direction_index + 1) % 4,  # sağa dön
            direction_index,            # düz git
            (direction_index - 1) % 4,  # sola dön
            (direction_index - 2) % 4   # geri dön
        ]
        
        moved = False
        
        for test_idx in test_order:
            test_direction = self.directions[test_idx]
            wall_name = self.direction_to_wall[test_direction]
            
            # Eğer o yönde duvar yoksa, hareket et
            if not self.current_cell.walls[wall_name]:
                dr, dc = self.direction_to_offset[test_direction]
                next_row, next_col = self.current_cell.row + dr, self.current_cell.col + dc
                
                # Sınırlar içinde mi?
                if 0 <= next_row < self.maze.rows and 0 <= next_col < self.maze.cols:
                    next_cell = self.maze.grid[next_row][next_col]
                    
                    # Hücreyi ziyaret et
                    next_cell.parent = self.current_cell  # Bu hücrenin parent'ı current_cell'dir
                    self.current_cell = next_cell
                    self.mark_visited(next_cell)
                    self.facing = test_direction
                    
                    # Ziyaret edilen hücreyi path'e ekle
                    self.path_cells.append(next_cell)
                    
                    moved = True
                    break
        
        # Eğer hiçbir yöne hareket edilemezse
        if not moved:
            self._is_finished = True
            print("WallFollower: Hareket edilecek yer kalmadı!")
            return True
        
        # Her adımdan sonra hedef kontrolü
        if self.current_cell == self.end_cell:
            self.solution_found = True
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            
            # Özel path takibimizi kullanarak reconstruct_path'i çağıralım
            self.reconstruct_path_from_visited()
            
            print("WallFollower: Hedef noktaya ulaşıldı!")
            return True
        
        return False
        
    def reconstruct_path_from_visited(self):
        """Ziyaret edilen hücrelerden oluşan path'i kullanarak çözüm yolunu oluştur."""
        if not self.solution_found:
            return
            
        # Önce tüm ziyaret izlerini temizle
        for row in self.maze.grid:
            for cell in row:
                cell.is_path = False
                cell.is_solution = False
        
        # Başlangıç ve bitiş hücrelerini tekrar işaretle
        self.start_cell.is_start = True
        self.end_cell.is_end = True
        
        # WallFollower'da daha doğru bir çözüm yolu oluşturmak için
        # ziyaret ettiğimiz tüm yolu biriktiriyoruz
        path = self.path_cells
        
        # Çözüm için ters yöne doğru yol bulma işlemi
        solution_path = []
        
        # Öncelikle end_cell'den başlayarak parent zincirini izleriz
        # Ancak bazen parent zinciri eksik olabileceği için biriktirdiğimiz path'ten faydalanırız
        current = self.end_cell
        
        # End_cell'i solution path'e ekleyelim
        solution_path.append(current)
        current.is_solution = True
        current.is_path = True
        
        # Path'in sonundan başlayarak end_cell'e kadar geri gidelim
        # Bu, duvar takip algoritmasının en doğru yol oluşturma şeklidir
        for i in range(len(path)-1, -1, -1):
            cell = path[i]
            
            # Eğer current'ın komşusuysa (aralarında duvar yoksa), bu solution path'in bir parçasıdır
            if self.are_neighbors(current, cell):
                cell.is_solution = True  # Çözüm yolunun bir parçası olarak işaretle
                cell.is_path = True      # Görünür path olarak da işaretle
                solution_path.append(cell)  # Çözüm yoluna ekle
                current = cell  # İlerlemeye devam et
                
                # Eğer start_cell'e ulaştıysak, tamamdır
                if cell == self.start_cell:
                    break
        
        # Başlangıç noktasını da çözüm yoluna ekle
        self.start_cell.is_solution = True
        self.start_cell.is_path = True
        
        # Yol uzunluğunu hesapla
        self.path_length = len(solution_path) - 1  # Start ve end arasındaki hücre sayısı
        
    def are_neighbors(self, cell1, cell2):
        """İki hücrenin komşu olup olmadığını kontrol eder (aralarında duvar yoksa)."""
        # İki hücrenin koordinatlarını kontrol ederek komşu olup olmadığını belirle
        dx = cell2.col - cell1.col
        dy = cell2.row - cell1.row
        
        # Eğer komşuysa (yan yana veya alt üst)
        if abs(dx) + abs(dy) == 1:
            # Aralarında duvar var mı kontrol et
            if dx == 1:  # cell2 sağda
                return not cell1.walls["right"] and not cell2.walls["left"]
            elif dx == -1:  # cell2 solda
                return not cell1.walls["left"] and not cell2.walls["right"]
            elif dy == 1:  # cell2 aşağıda
                return not cell1.walls["bottom"] and not cell2.walls["top"]
            elif dy == -1:  # cell2 yukarıda
                return not cell1.walls["top"] and not cell2.walls["bottom"]
        
        return False

class Dijkstra(MazeSolvingAlgorithm):
    """Dijkstra'nın En Kısa Yol Algoritması."""
    
    def __init__(self, maze):
        super().__init__(maze)
        self.name = "Dijkstra"
        self.priority_queue = []
        self.visited = set()
    
    def initialize(self):
        super().initialize()
        
        # Başlangıç hücresini kuyruğa ekle (öncelik, hücre)
        self.start_cell.distance = 0
        self.priority_queue = []  # Kuyruğu temizle
        # Başlangıç hücresini kuyruğa ekle ve ID ekleyerek benzersiz sıralama sağla
        heapq.heappush(self.priority_queue, (0, id(self.start_cell), self.start_cell))  
        self.visited = set()
    
    def step(self):
        if super().step():
            return True
        
        if not self.priority_queue:
            self._is_finished = True
            return True
        
        # En düşük maliyetli hücreyi kuyruğun başından al
        current_distance, _, current = heapq.heappop(self.priority_queue)
        
        # Hedef hücreye ulaşıldı mı kontrol et
        if current == self.end_cell:
            self.solution_found = True
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            self.reconstruct_path()
            return True
            
        # Zaten ziyaret edilmişse adımı atla
        if current in self.visited:
            return False
        
        # Hücreyi ziyaret et
        self.visited.add(current)
        self.mark_visited(current)
        self.current_cell = current
        
        # Komşulara bak - sadece duvarsız bağlantıları kontrol et
        for neighbor in current.get_neighbors(self.maze.grid, include_walls=False):
            if neighbor not in self.visited:
                # Yeni mesafeyi hesapla (her adım 1 birim)
                new_distance = current_distance + 1
                
                # Daha iyi bir yol bulduysa güncelle
                if new_distance < neighbor.distance:
                    neighbor.distance = new_distance
                    neighbor.parent = current
                    # ID ile benzersiz sıralama sağla
                    heapq.heappush(self.priority_queue, (new_distance, id(neighbor), neighbor))
        
        return False

class DeadEndFilling(MazeSolvingAlgorithm):
    """Çıkmaz Sokak Doldurma Algoritması."""
    
    def __init__(self, maze):
        super().__init__(maze)
        self.name = "Çıkmaz Doldurma"
        self.dead_ends = []
        self.current_index = 0
    
    def initialize(self):
        super().initialize()
        
        # Çıkmaz sokakları bul
        self.dead_ends = []
        for row in self.maze.grid:
            for cell in row:
                # Başlangıç ve bitiş hücresini atla
                if cell == self.start_cell or cell == self.end_cell:
                    continue
                
                # Tek bir çıkışı olan hücreler çıkmaz sokaktır
                # Sadece duvarsız bağlantıları kontrol et
                neighbors = cell.get_neighbors(self.maze.grid, include_walls=False)
                if len(neighbors) == 1:
                    self.dead_ends.append(cell)
        
        self.current_index = 0
    
    def step(self):
        if super().step():
            return True
        
        if self.current_index >= len(self.dead_ends):
            print(f"Çıkmaz Doldurma: {len(self.dead_ends)} adet çıkmaz sokak dolduruldu.")
            # Tüm çıkmaz sokaklar işlendi, şimdi başlangıçtan bitişe DFS ile yol bul
            dfs = DFS(self.maze)
            dfs.initialize()
            
            # DFS algoritmasını tamamen çalıştır
            dfs_step_count = 0
            max_steps = self.maze.rows * self.maze.cols * 4  # Maximum adım sayısı sınırı
            
            while not dfs._is_finished and dfs_step_count < max_steps:
                dfs.step()
                dfs_step_count += 1
            
            # DFS'den çözüm yolunu al
            if dfs.solution_found:
                # Çözüm bulunduğunda, çözüm verilerini kopyala
                self.solution_found = True
                self.path_length = dfs.path_length
                self.visited_count = dfs.visited_count + self.visited_count
                
                # Hücreleri doğrudan bizim algoritma sonucu olarak işaretle
                for row in self.maze.grid:
                    for cell in row:
                        # Önce tüm ziyaret işaretlemelerini kaldır
                        cell.is_path = False
                        
                # Sadece çözüm yolundaki hücreleri işaretle
                current = self.maze.end_cell
                while current and current != self.maze.start_cell:
                    current.is_solution = True
                    current.is_path = True
                    current = current.parent
                
                # Başlangıç noktasını da işaretle
                if self.maze.start_cell:
                    self.maze.start_cell.is_solution = True
                    self.maze.start_cell.is_path = True
                
                print(f"Çıkmaz Doldurma: DFS ile çözüm bulundu. Yol uzunluğu: {self.path_length}")
            else:
                print("Çıkmaz Doldurma: DFS ile çözüm bulunamadı!")
            
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            return True
        
        # Çıkmaz sokakları doldur - her adımda bir çıkmaz sokağı işaretle
        current_dead_end = self.dead_ends[self.current_index]
        self.current_cell = current_dead_end
        self.mark_visited(current_dead_end)
        
        # Bu hücreden tek çıkışı bul ve önceki olarak ayarla
        # Sadece duvarsız bağlantıları kontrol et
        neighbors = current_dead_end.get_neighbors(self.maze.grid, include_walls=False)
        if neighbors:
            current_dead_end.parent = neighbors[0]
        
        # Bir sonraki çıkmaz sokağa geç
        self.current_index += 1
        
        return False

class BFS(MazeSolvingAlgorithm):
    """Genişlik Öncelikli Arama Algoritması."""
    
    def __init__(self, maze):
        super().__init__(maze)
        self.name = "BFS"
        self.queue = deque()
    
    def initialize(self):
        super().initialize()
        
        # Kuyruğu temizle
        self.queue = deque()
        # Başlangıç hücresini kuyruğa ekle
        self.queue.append(self.start_cell)
        self.visited_cells = set([self.start_cell])
        self.start_cell.visited = True
    
    def step(self):
        if super().step():
            return True
        
        if not self.queue:
            self._is_finished = True
            return True
        
        # Kuyruktan bir hücre al
        current = self.queue.popleft()
        self.current_cell = current
        
        # Hedef hücreye ulaşıldı mı kontrol et
        if current == self.end_cell:
            self.solution_found = True
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            self.reconstruct_path()
            return True
        
        # Komşulara bak - sadece duvarsız bağlantıları kontrol et
        for neighbor in current.get_neighbors(self.maze.grid, include_walls=False):
            if neighbor not in self.visited_cells:
                neighbor.visited = True
                neighbor.is_path = True
                neighbor.parent = current
                self.visited_cells.add(neighbor)
                self.visited_count += 1
                self.queue.append(neighbor)
        
        return False

class DFS(MazeSolvingAlgorithm):
    """Derinlik Öncelikli Arama Algoritması."""
    
    def __init__(self, maze):
        super().__init__(maze)
        self.name = "DFS"
        self.stack = []
    
    def initialize(self):
        super().initialize()
        
        # Yığını temizle
        self.stack = []
        # Başlangıç hücresini yığına ekle
        self.stack.append(self.start_cell)
        self.visited_cells = set([self.start_cell])
        self.start_cell.visited = True
    
    def step(self):
        if super().step():
            return True
        
        if not self.stack:
            self._is_finished = True
            return True
        
        # Yığından bir hücre al
        current = self.stack.pop()
        self.current_cell = current
        
        # Hedef hücreye ulaşıldı mı kontrol et
        if current == self.end_cell:
            self.solution_found = True
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            self.reconstruct_path()
            return True
        
        # Komşulara bak - sadece duvarsız bağlantıları kontrol et
        for neighbor in current.get_neighbors(self.maze.grid, include_walls=False):
            if neighbor not in self.visited_cells:
                neighbor.visited = True
                neighbor.is_path = True
                neighbor.parent = current
                self.visited_cells.add(neighbor)
                self.visited_count += 1
                self.stack.append(neighbor)
        
        return False

class IDS(MazeSolvingAlgorithm):
    """Yinelemeli Derinleştirme Arama Algoritması."""
    
    def __init__(self, maze):
        super().__init__(maze)
        self.name = "IDS"
        self.max_depth = 0
        self.current_depth = 0
        self.stack = []
        self.depths = {}  # Her hücrenin derinliğini tut
    
    def initialize(self):
        super().initialize()
        
        # Başlangıç değerlerini ayarla
        self.max_depth = 0
        self.current_depth = 0
        
        # Yığını temizle
        self.stack = []
        # Başlangıç hücresini yığına ekle
        self.stack.append((self.start_cell, 0))  # (hücre, derinlik)
        self.depths = {self.start_cell: 0}
        self.start_cell.visited = True
    
    def step(self):
        if super().step():
            return True
        
        if not self.stack:
            # Yığın boşsa, derinliği artır ve yeniden başla
            self.max_depth += 1
            
            # Belli bir derinlikten sonra sonlandır
            if self.max_depth > self.maze.rows * self.maze.cols:
                self._is_finished = True
                return True
            
            # Hücreleri sıfırla
            for row in self.maze.grid:
                for cell in row:
                    cell.reset_path_data()
            
            # Başlangıç hücresini yığına ekle
            self.stack = [(self.start_cell, 0)]
            self.depths = {self.start_cell: 0}
            self.visited_cells = set([self.start_cell])
            self.start_cell.visited = True
            return False
        
        # Yığından bir hücre al
        current, depth = self.stack.pop()
        self.current_cell = current
        self.current_depth = depth
        
        # Hedef hücreye ulaşıldı mı kontrol et
        if current == self.end_cell:
            self.solution_found = True
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            self.reconstruct_path()
            return True
        
        # Eğer mevcut derinlik maksimum derinlikten küçükse komşulara bak
        if depth < self.max_depth:
            # Sadece duvarsız bağlantıları kontrol et
            for neighbor in current.get_neighbors(self.maze.grid, include_walls=False):
                new_depth = depth + 1
                
                # Daha önce ziyaret edilmemiş veya daha düşük derinlikte ziyaret edilmiş ise
                if neighbor not in self.visited_cells or new_depth < self.depths.get(neighbor, float('inf')):
                    neighbor.visited = True
                    neighbor.is_path = True
                    neighbor.parent = current
                    self.visited_cells.add(neighbor)
                    self.visited_count += 1
                    self.depths[neighbor] = new_depth
                    self.stack.append((neighbor, new_depth))
        
        return False

class AStar(MazeSolvingAlgorithm):
    """A* Arama Algoritması."""
    
    def __init__(self, maze):
        super().__init__(maze)
        self.name = "A*"
        self.open_set = []
        self.closed_set = set()
        self.g_score = {}  # Başlangıçtan bir hücreye en kısa yol maliyeti
        self.f_score = {}  # g_score + heuristic (tahmin edilen maliyet)
    
    def initialize(self):
        super().initialize()
        
        # Başlangıç hücresini açık sete ekle
        self.start_cell.distance = 0
        self.g_score = {self.start_cell: 0}
        
        # Manhattan mesafesini kullanarak f-skoru hesapla
        start_heuristic = self.heuristic(self.start_cell)
        self.f_score = {self.start_cell: start_heuristic}
        
        # Açık seti temizle
        self.open_set = []
        heapq.heappush(self.open_set, (self.f_score[self.start_cell], 0, self.start_cell))  # (f_score, tie_breaker, cell)
        self.closed_set = set()
    
    def heuristic(self, cell):
        """Manhattan mesafesi hesapla."""
        return abs(cell.row - self.end_cell.row) + abs(cell.col - self.end_cell.col)
    
    def step(self):
        if super().step():
            return True
        
        if not self.open_set:
            self._is_finished = True
            return True
        
        # En düşük f-skora sahip hücreyi al
        _, _, current = heapq.heappop(self.open_set)
        self.current_cell = current
        
        # Hedef hücreye ulaşıldı mı kontrol et
        if current == self.end_cell:
            self.solution_found = True
            self._is_finished = True
            self.elapsed_time = time.time() - self.start_time
            self.reconstruct_path()
            return True
        
        # Kapalı sete ekle
        self.closed_set.add(current)
        self.mark_visited(current)
        
        # Komşulara bak - sadece duvarsız bağlantıları kontrol et
        for neighbor in current.get_neighbors(self.maze.grid, include_walls=False):
            if neighbor in self.closed_set:
                continue
            
            # Komşuya gitmek için tentative_g_score hesapla
            tentative_g_score = self.g_score[current] + 1  # Her adım 1 birim
            
            # Komşu açık sette değilse veya daha iyi bir g-skor bulduysa
            if neighbor not in self.g_score or tentative_g_score < self.g_score[neighbor]:
                # Bu yol en iyiyse, kaydediyoruz
                neighbor.parent = current
                self.g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + self.heuristic(neighbor)
                self.f_score[neighbor] = f_score
                
                # Eşitlik durumunda rastgele sıralama için tie_breaker
                tie_breaker = random.random()
                
                # Açık sete ekle
                if neighbor not in [cell for _, _, cell in self.open_set]:
                    heapq.heappush(self.open_set, (f_score, tie_breaker, neighbor))
        
        return False

def create_algorithm(algo_name, maze=None):
    """Algoritma adına göre uygun algoritmayı oluştur."""
    if not maze:
        # Sadece karşılaştırma seçimi için boş bir şablon döndür
        return {"name": algo_name}
    
    algorithms = {
        "wall_follower": WallFollower,
        "dijkstra": Dijkstra,
        "dead_end_filling": DeadEndFilling,
        "bfs": BFS,
        "dfs": DFS,
        "ids": IDS,
        "a_star": AStar
    }
    
    if algo_name in algorithms:
        return algorithms[algo_name](maze)
    
    # Varsayılan olarak BFS
    return BFS(maze)
