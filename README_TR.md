# Labirent Çözücü Görselleştirici

Bu proje, Python ve Pygame kullanılarak geliştirilmiş interaktif bir labirent çözücü uygulamasıdır. Farklı labirent oluşturma ve çözme algoritmalarını görselleştirmenize ve karşılaştırmanıza olanak tanır.

## Özellikler

- **Labirent Oluşturma**: İki farklı algoritma ile rastgele labirentler oluşturabilirsiniz:
  - Recursive Backtracking (Özyinelemeli Geri İzleme)
  - Prim's Algorithm (Prim Algoritması)

- **Labirent Çözme**: Yedi farklı algoritma ile labirenti çözebilirsiniz:
  - Wall Follower (Duvar Takibi)
  - Dijkstra's Algorithm (Dijkstra Algoritması)
  - Dead End Filling (Çıkmaz Sokak Doldurma)
  - BFS (Breadth-First Search - Genişlik Öncelikli Arama)
  - DFS (Depth-First Search - Derinlik Öncelikli Arama)
  - IDS (Iterative Deepening Search - Yinelemeli Derinleştirme Arama)
  - A* (A Yıldız)

- **Algoritma Karşılaştırması**: İki ile dört arasında algoritmayı yan yana karşılaştırabilir, performanslarını ve verimliliğini gözlemleyebilirsiniz.

- **Görselleştirme**: Tüm algoritmalar adım adım görselleştirilir:
  - Yeşil: Başlangıç noktası
  - Kırmızı: Bitiş noktası
  - Mavi: Ziyaret edilen hücreler
  - Sarı: Bulunan çözüm yolu
  - Kırmızı Nokta: İşlem yapılan mevcut hücre

## Gereksinimler

- Python 3.6 veya üzeri
- pygame
- numpy

## Kurulum

1. Projeyi klonlayın veya indirin
2. Gerekli paketleri yükleyin:

```
pip install -r requirements.txt
```

## Kullanım

Programı başlatmak için:

```
python main.py
```

### Ana Menü

Ana menüden şu işlemleri yapabilirsiniz:

1. **Labirent Oluştur**: Yeni bir labirent oluşturmak için algoritma seçin ve boyutu ayarlayın.
2. **Labirenti Çöz**: Mevcut labirenti çözmek için bir algoritma seçin.
3. **Algoritmaları Karşılaştır**: Farklı algoritmaları yan yana karşılaştırmak için 2-4 algoritma seçin.
4. **Çıkış**: Programdan çıkın.

### Kontroller

- **ESC**: Ana menüye dön
- **SPACE**: Algoritma çalışmasını duraklat/devam ettir (çözme ve karşılaştırma modlarında)

## Proje Yapısı

- `main.py`: Ana program dosyası
- `maze.py`: Labirent sınıfı ve oluşturma algoritmaları
- `algorithms.py`: Labirent çözme algoritmaları
- `ui.py`: Kullanıcı arayüzü bileşenleri

## Algoritmalar Hakkında

### Labirent Oluşturma

- **Recursive Backtracking**: Derinlik öncelikli arama kullanan bir algoritma. Rasgele yönlerde ilerleyerek ve çıkmaza girdiğinde geri izleme yaparak labirenti oluşturur.
- **Prim's Algorithm**: Minimum kapsayan ağaç algoritması. Rasgele bir hücreden başlar ve sınır hücrelerini ekleyerek labirenti oluşturur.

### Labirent Çözme

- **Wall Follower**: Sağ (veya sol) el kuralını kullanarak duvarları takip eder. Tüm labirentlerde çalışmaz, sadece "basit bağlantılı" labirentlerde çözüm bulabilir.
- **Dijkstra**: En kısa yolu bulmak için tüm olası yolları değerlendirir. Kesin olarak en kısa yolu bulur.
- **Dead End Filling**: Çıkmaz sokakları doldurarak ana yolu bulmayı amaçlar. Basit labirentlerde etkilidir.
- **BFS**: Genişlik öncelikli arama, en kısa yolu bulmak için tüm yolları eşit şekilde genişletir.
- **DFS**: Derinlik öncelikli arama, bir yolu sonuna kadar takip eder, çıkmaza girerse geri döner.
- **IDS**: Derinlik sınırlı DFS'yi artan derinliklerle uygular. BFS gibi en kısa yolu bulur ama daha az bellek kullanır.
- **A***: Hedefe olan tahmini mesafeyi (sezgisel) kullanarak Dijkstra algoritmasını geliştirir. Genellikle Dijkstra'dan daha hızlıdır. 