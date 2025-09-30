# Space Shooter Project (CSLT)

## Giới thiệu học thuật

Đồ án "Space Shooter" được xây dựng trong khuôn khổ môn Cơ sở Lập trình (CSLT). Mục tiêu của dự án là giúp sinh viên vận dụng kiến thức lập trình Python kết hợp với thư viện Pygame để phát triển một trò chơi 2D hoàn chỉnh. Thông qua quá trình thực hiện, sinh viên có cơ hội:

* Hiểu và áp dụng khái niệm vòng lặp trò chơi (game loop) và xử lý sự kiện (event handling).
* Vận dụng lập trình hướng đối tượng trong thiết kế nhân vật, kẻ địch, và hệ thống điểm số.
* Làm quen với cách quản lý tài nguyên đa phương tiện (hình ảnh, âm thanh, font chữ).
* Rèn luyện kỹ năng tư duy logic, giải quyết vấn đề và sáng tạo trong phát triển tính năng.
  Dự án không chỉ phục vụ mục tiêu học tập mà còn tạo nền tảng để mở rộng sang các ứng dụng phức tạp hơn trong phát triển game và phần mềm.

## Mô tả

Space Shooter Project phát triển bằng Python và Pygame. Người chơi điều khiển một phi thuyền trong không gian, bắn hạ kẻ địch, tránh chướng ngại vật và ghi điểm cao nhất có thể. Trò chơi được thiết kế để minh họa các khái niệm cơ bản trong lập trình game 2D.

## Tính năng

* Lối chơi bắn súng không gian cổ điển.
* Phi thuyền có khả năng di chuyển và bắn.
* Nhiều loại kẻ địch: thiên thạch, ngôi sao.
* Hiệu ứng âm thanh: bắn, trúng đạn, nổ.
* Nhạc nền tạo sự lôi cuốn.
* Hệ thống tính điểm và lưu điểm cao.
* Có thể mở rộng với màn chơi trùm cuối.
* Đồ họa dạng pixel và sử dụng font tùy chỉnh.

## Cấu trúc dự án
```
Space_Shooter_Project/
│── .gitignore              # Quy tắc bỏ qua file của Git
│── Testgame/               # Thư mục chứa code chính (PyCharm)
│── pyvenv.cfg              # Cấu hình môi trường ảo
│── highscore.txt           # Lưu điểm cao
│
├── Assets/
│   ├── damage.ogg          # Âm thanh khi bị trúng
│   ├── explosion.wav       # Âm thanh nổ
│   ├── game_music.wav      # Nhạc nền
│   ├── laser.png           # Hình ảnh đạn laser
│   ├── laser.wav           # Âm thanh bắn
│   ├── meteor.png          # Hình ảnh thiên thạch
│   ├── player.png          # Hình ảnh phi thuyền
│   ├── star.png            # Hình ảnh ngôi sao
│   ├── Oxanium-Bold.ttf    # Font chữ
└── Testgame.py             # File code main và khởi động Pygame
```
## Yêu cầu hệ thống

* Python 3.8 trở lên
* Thư viện Pygame

Cài đặt thư viện:

```bash
pip install pygame
```

## Hướng dẫn chạy

1. Tải về repository:

```bash
git clone https://github.com/OanhNguyen90/Space_Shooter_Project_Game_Development_CSLT.git
cd Space_Shooter_Project_Game_Development_CSLT
```

2. Tạo và kích hoạt môi trường ảo (khuyến nghị):

```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

3. Chạy trò chơi:

```bash
python Testgame/main.py
```

## Điều khiển

* Phím mũi tên hoặc WASD: di chuyển phi thuyền
* Space: bắn
* P: tạm dừng
* ESC: trở về menu chính

## Hệ thống tính điểm

* Phá hủy thiên thạch: +10 điểm
* Nhặt vật phẩm xanh: +20 điểm
* Tránh va chạm để sống lâu hơn
* Điểm cao lưu trong file `highscore.txt`

## Tài nguyên

* Âm thanh: damage.ogg, explosion.wav, laser.wav, game\_music.wav
* Font chữ: Oxanium-Bold.ttf
* Hình ảnh: phi thuyền, thiên thạch, sao, đạn laser, Boss, NPC (caption), background, những vật phẩm xanh, đạn rác từ Boss

## Hướng phát triển

* Thêm nhiều loại kẻ địch
* Tích hợp hệ thống vật phẩm hỗ trợ
* Nâng cấp màn chơi trùm cuối
* Tích hợp bảng xếp hạng trực tuyến
* Tích hợp thêm phần Save Game
* Tích hợp thêm nhiều người chơi trong cùng 1 trò/ chơi online

## Giấy phép

Dự án sử dụng giấy phép Apache License 2.0. Xem chi tiết trong file LICENSE.
