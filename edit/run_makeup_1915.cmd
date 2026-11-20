@echo off
chcp 65001 >nul
timeout /t 20 /nobreak >nul
if not exist "Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\mẹ chồng trọng nam khinh nữ.mp4" exit /b 0
if exist "D:\AI\full studio\edit\.tiktok_post.lock" exit /b 0
"C:\Program Files\nodejs\node.exe" "D:\AI\full studio\edit\tiktok_brave_post.mjs" --post --force --file "Z:\Máy tính khác\My Computer\hằng thu pharma\05. Video Hoàn Thiện\K4 - Mẹ Chồng Nàng Dâu\đã đăng\mẹ chồng trọng nam khinh nữ.mp4" --caption "Mẹ chồng trọng nam khinh nữ - Đỉnh cao của sự thiên vị khiến nhà cửa lúc nào cũng sóng gió! Xem mà tức thay cho cô con dâu... 😤 Các bác xem xong đoạn này thấy thế nào? #MeChongNangDau #PhimNgan #PhimDrama #DramaGiaDinh #PhimViet" --cover "D:\AI\full studio\edit\cover_me_chong_trong_nam.png" >> "D:\AI\full studio\edit\tiktok_autopost.log" 2>&1
