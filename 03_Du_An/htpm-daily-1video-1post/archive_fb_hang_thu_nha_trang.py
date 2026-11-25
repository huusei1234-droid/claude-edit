# -*- coding: utf-8 -*-
"""
Tải & Lưu trữ toàn bộ 16 ảnh gốc độ phân giải cao (960px - 2048px) + ảnh chụp lưới Reels/Albums + Hồ sơ DNA Nhân vật
từ trang Facebook cá nhân của CEO Nguyễn Thị Hằng (https://www.facebook.com/hang.thu.146 — Sống tại Nha Trang)
vào cả 3 nơi chuẩn quy tắc GEMINI.md Rule #2.0:
1. Brand Kit Local: d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma\ambassadors_models\FB_Hang_Thu_146_Nha_Trang\
2. Hồ Sơ Khách Hàng Google Drive: Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\00_Ho_So_Thuong_Hieu_Va_Tham_Khao\FB_Hang_Thu_146_Nha_Trang\
3. Kho Media TLH\Edit: Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\08_Brand Kits Thương Hiệu & Ảnh PNG\01_HTPM_Hang_Thu_Pharma\ambassadors_models\FB_Hang_Thu_146_Nha_Trang\
"""
import json
import os
import shutil
import urllib.request
from pathlib import Path
from PIL import Image, ImageOps

LOCAL_DIR = Path(r"d:\AI\full studio\BO_KIEN_THUC_TVC_AI_PORTABLE\03_TAI_NGUYEN_DUNG_CHUNG\brand_kits\01_HTPM_Hang_Thu_Pharma\ambassadors_models\FB_Hang_Thu_146_Nha_Trang")
DRIVE_CUST_DIR = Path(r"Z:\.shortcut-targets-by-id\1qjnlz_54ZT5OlI9dKMelZ5PJauD4etj-\hằng thu pharma\00_Ho_So_Thuong_Hieu_Va_Tham_Khao\FB_Hang_Thu_146_Nha_Trang")
DRIVE_TLH_DIR = Path(r"Z:\Máy tính khác\My Computer\Document HT Media\TLH\Edit\08_Brand Kits Thương Hiệu & Ảnh PNG\01_HTPM_Hang_Thu_Pharma\ambassadors_models\FB_Hang_Thu_146_Nha_Trang")
ARTIFACT_DIR = Path(r"C:\Users\Hang thu\.gemini\antigravity\brain\61a8cd03-a271-41c6-b4d7-d5c1b7fe3682")

SANDBOX_SHOTS = [
    (r"C:\Users\Hang thu\.gemini\antigravity\brain\aec06662-16a4-41d2-abca-d43838174af5\browser_sandbox\screenshots\step_44.png", "FB_Grid_01_Wardrobe_Variety.png"),
    (r"C:\Users\Hang thu\.gemini\antigravity\brain\aec06662-16a4-41d2-abca-d43838174af5\browser_sandbox\screenshots\step_48.png", "FB_Grid_02_Vinpearl_Nha_Trang.png"),
    (r"C:\Users\Hang thu\.gemini\antigravity\brain\aec06662-16a4-41d2-abca-d43838174af5\browser_sandbox\screenshots\step_67.png", "FB_Grid_03_Reels_Nha_Trang_Lifestyle.png"),
]

PHOTOS = [
    ("01_ceo_white_draped_blazer_office.jpg", "Vest trắng khoác hờ vai sang trọng tại phòng điều hành đá sáng", "https://scontent.fsgn2-10.fna.fbcdn.net/v/t39.99422-6/814929899_4049211198705378_7839809353276872322_n.png?stp=dst-jpg_tt6&cstp=mx960x960&ctp=s960x960&_nc_cat=105&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=6ee11a&_nc_eui2=AeFpKOyfhW-Jhny5w8JjaEiK3daJWmAq9Knd1olaYCr0qTPSrf__uPzUoIKhD_vgiYT2O5aiHvM1_Nn4dx6rXpTv&_nc_ohc=Y_g2SmLAvfsQ7kNvwFmp_-U&_nc_oc=AdrddNNwIFHpZoux_8nxjjx56xLUKNNhN50_VhiBd5W9Y6Buv_xq0rLoISF4dyv2emdVWdgcWxC1oRjM_vc7m1rh&_nc_zt=14&_nc_ht=scontent.fsgn2-10.fna&_nc_gid=J4xrcY9eDCrpgrnHm3zWtw&_nc_ss=793a8&oh=00_AQTV1101Dfz3vHtWSuNmuqVCVvHIm9WX_XwwkEt2UdcRwA&oe=6B0B281B"),
    ("02_cream_pearl_cape_blazer_lounge.jpg", "Đầm kem đính ngọc trai & áo choàng cài hoa hồng trắng thanh lịch", "https://scontent.fsgn2-11.fna.fbcdn.net/v/t39.99422-6/803323540_1592488682322842_6941912396293145402_n.png?stp=dst-jpg_tt6&cstp=mx960x960&ctp=s960x960&_nc_cat=110&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeH10VZqL41YqpnHYDZmQPuCsy3IVqlmx2KzLchWqWbHYpxI5qpCZjMicHYcHPNw5TOYRJ0y_rtsTRy8ex7Cmwuq&_nc_ohc=fHqOBGHs0q8Q7kNvwEn5Oie&_nc_oc=AdoSylz5BlHk2JQ9GWOozcWyAGzW1gzWLhIYar-sFU9iMYqWmo5rPiSG5L54sVvUaMg9V4wJSnZbHN3eR32QZeZ3&_nc_zt=14&_nc_ht=scontent.fsgn2-11.fna&_nc_gid=5RyY4Ox_E4OCtaOYxnX-5w&_nc_ss=793a8&oh=00_AQSWKWaNlW4_E58pA17PjFvW_Nx40rD7hu5tgN-xu_ZdYA&oe=6B0B3803"),
    ("03_crimson_red_suit_ceo_desk.jpg", "Suit đỏ đô quyền lực ngồi bàn điều hành CEO", "https://scontent.fsgn2-11.fna.fbcdn.net/v/t39.99422-6/796725855_1589660602894402_5412776338184893096_n.png?stp=dst-jpg_tt6&cstp=mx960x960&ctp=s960x960&_nc_cat=110&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeEyB8ynA-EvfJNUaibDhGvpI8rMWZHa10ojysxZkdrXSiCtdpGAS-2ZFuYk1tjJYopiER8YP_erkPnufCXSj6qQ&_nc_ohc=yunyTZRFF0kQ7kNvwHPve0W&_nc_oc=AdpFKjnFcxDWLKDRQKa4cu_uPcDONTebwp-4eN3l7CGFo5Ma-4ac2-G7VzINIxwqr2JcuHOHqW0oWQl5vtxiW9Jp&_nc_zt=14&_nc_ht=scontent.fsgn2-11.fna&_nc_gid=sQUNegvYwMfpeT2hBSwwzA&_nc_ss=793a8&oh=00_AQR1iRcxbolfd6IjNn3gz012weeD23PeC9GNJG-T_X2v0g&oe=6B0B58A2"),
    ("04_royal_blue_ao_dai_stage.jpg", "Áo dài xanh dương đính kim sa truyền lửa trên sân khấu", "https://scontent.fsgn2-3.fna.fbcdn.net/v/t39.30808-6/515382045_24213254241644655_3366384323368482735_n.jpg?stp=dst-jpg_tt6&cstp=mx1440x1440&ctp=s1440x1440&_nc_cat=110&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeHJOHKmS_XiF1qx16y4WiaU_byrUrudfDj9vKtSu518OPdoC2ygePvB3CnluXDYlgsfrFFOBVOYN29oBk4ANaxg&_nc_ohc=mVvMC5ZqLgYQ7kNvwFRKLtS&_nc_oc=Adq8v4ndLkx0i8wTnSS7rH1MFLtP8xztkbjnsd3dGjFx0DI-OMqg6Kmh7HVy4VSZkDNQU5RDE4qQYWmQay3hq4Np&_nc_zt=23&_nc_ht=scontent.fsgn2-3.fna&_nc_gid=T5juwBJWov1Se3ZYxU_7Sw&_nc_ss=793a8&oh=00_AQR9asiY79j6g1ykWvuoSsuiiXj7mTkVEEIkLORTQl8yNg&oe=6B0B284D"),
    ("05_beige_blazer_bni_nha_trang.jpg", "Blazer kem thanh lịch tại sự kiện doanh nhân BNI Nha Trang", "https://scontent.fsgn2-10.fna.fbcdn.net/v/t39.30808-6/490482853_9820560134673972_4509419144192332579_n.jpg?stp=dst-jpg_tt6&cstp=mx1364x1364&ctp=s1364x1364&_nc_cat=108&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeESs6LUEzIbTinE_SyM0BwZr10ELFu9WOKvXQQsW71Y4h-VVFz3u6qBHGeQLkKCrX2AI_r9Txzi-PyvoXF13KVq&_nc_ohc=zdws5f6ahPIQ7kNvwFksGjU&_nc_oc=AdoIQxL6NtaIkwcvevLnvQmMChb7hFAOx0lNthykIVLgqCqOpsy1ulF4wMUdvZkPn2m8blngRvhFZROayDFNerLA&_nc_zt=23&_nc_ht=scontent.fsgn2-10.fna&_nc_gid=qh-1rnfxMxWRTATXXSSl5w&_nc_ss=793a8&oh=00_AQSwWrf-pHWY8rZEk0Rjs7E9W3gWSQGkO57u_lQyu-9dsQ&oe=6B0B51F5"),
    ("06_black_evening_dress_floral_choker.jpg", "Đầm đen trễ vai búi tóc thấp sang trọng trong trẻo", "https://scontent.fsgn2-6.fna.fbcdn.net/v/t39.30808-6/5025288884_23965772629726152_4104993081065968532_n.jpg".replace("5025288884", "502528884") + "?stp=dst-jpg_tt6&cstp=mx960x960&ctp=s960x960&_nc_cat=100&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeF7wmwNeMQ7I7ZY8Vfsp088DMHmwZVL4O4MwebBlUvg7mIOljfQToPKhhaANPHsGj9TDVab91-xCF6OlQ25Aw7L&_nc_ohc=6qV28wYIPeUQ7kNvwHeN-QR&_nc_oc=Adqu_-BHMXxMuLMLPvEO0KQWiWOrQ0kHwKPwD8ARUVMwqNeYcBZpcLRVfFnJ5xBr3ZvRPS2GPEjFWdgul-S9w8xp&_nc_zt=23&_nc_ht=scontent.fsgn2-6.fna&_nc_gid=wejq6lys1-ZbSmeSvuMEJg&_nc_ss=793a8&oh=00_AQSiNB1euNy1Yd2kDUmt9DvMywnNiycL-yYmk0ygsxgjYw&oe=6B0B51E8"),
    ("07_navy_blazer_pearl_necklace.jpg", "Vest xanh navy phối chuỗi ngọc trai cổ điển", "https://scontent.fsgn2-5.fna.fbcdn.net/v/t39.30808-6/497632707_10057205911009392_3299851882205281590_n.jpg?stp=dst-jpg_tt6&cstp=mx854x855&ctp=s854x855&_nc_cat=104&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeH4ydtmwuC5ZLTK4cSJcggJQFTC8J5dmopAVMLwnl2aikLWq8TZJiQ_NUS4O0RXytZv6jOzjVvfiQ2tjQbZ1k4_&_nc_ohc=3KgT1ZwplWwQ7kNvwHHn_ES&_nc_oc=Ado6WVA1GcuF0HcP4RFqA-eTejjw7Z5gveEXk2HxcP-AZVDMrY0NECR0ZXEGy6dXmSGWcumn9NzJkke_UrSY7eP5&_nc_zt=23&_nc_ht=scontent.fsgn2-5.fna&_nc_gid=iKzfziskn_6YnxCfb3IQfA&_nc_ss=793a8&oh=00_AQS-aq5GYXrW3PiSX19xBuuLjgrgPwmKebCDtVNBd7ue8w&oe=6B0B4C27"),
    ("08_pastel_ice_blue_ruffle_dress.jpg", "Đầm xanh băng pastel trễ vai tươi tắn rạng rỡ", "https://scontent.fsgn2-5.fna.fbcdn.net/v/t39.30808-6/496803890_10050719151658068_5883261316580636813_n.jpg?stp=dst-jpg_tt6&cstp=mx1365x1366&ctp=s1365x1366&_nc_cat=101&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeE4CQ6ChdwelvZF09LQqlq0SxnWXEhGiwJLGdZcSEaLAmcOamnLVYqYhJiHf2cPFfsXGYFAf9GI6fgV8L0Ple-Y&_nc_ohc=wCBI6IVjcdQQ7kNvwEe4cwa&_nc_oc=AdpyTCIgcsRhAce6ndVoQT4M2cBl756qUWrzudV-6oDhoZWWPt80V2dfyfL07yaKO5Np6GsPNYmtdrCIxKkWncJP&_nc_zt=23&_nc_ht=scontent.fsgn2-5.fna&_nc_gid=ujYujMX0eCsUmej-UkPmOg&_nc_ss=793a8&oh=00_AQR9FvAYGs2sfX9OI3LAXG-nLOn2InR_ElPQvBwC7QuEYg&oe=6B0B498E"),
    ("09_lime_green_modern_suit.jpg", "Suit xanh cốm trẻ trung năng động", "https://scontent.fsgn2-3.fna.fbcdn.net/v/t39.30808-6/486423230_9717399188323401_4423612238229298902_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x2048&ctp=s2048x2048&_nc_cat=109&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeEhmfz40IOcA7MI53JrhfjVzmN9VUZcZa3OY31VRlxlrflehSMuG78MnoX0xI_axdwRG70BysZMRuLJ7YutJGsx&_nc_ohc=dmf4EeROcbgQ7kNvwEBx8un&_nc_oc=AdrU2qR4ZHb8Jt2ofLVOa6otJognenx1FUh2J-a2ynz-6ccLGGC9BPcbX1PQSg0BJLm_YzTprPtSgMZBVns5bnNU&_nc_zt=23&_nc_ht=scontent.fsgn2-3.fna&_nc_gid=OyUKvCxtZXzfv9BjpJGh5Q&_nc_ss=793a8&oh=00_AQRFIsC16HMdPwx7nHGhTEXsJKC6P0xeh7uOuWOAded5vw&oe=6B0B2E96"),
    ("10_white_belted_blazer_dress_sunlit.jpg", "Đầm vest trắng chiết eo dưới nắng sớm qua rèm cửa trong trẻo", "https://scontent.fsgn2-10.fna.fbcdn.net/v/t39.30808-6/481231898_9537248839671771_3001856233814748957_n.jpg?stp=dst-jpg_tt6&cstp=mx960x960&ctp=s960x960&_nc_cat=107&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeGbkxsyY-hpf3l4CvAEU0fZ1_i1dgsYbQ_X-LV2CxhtD0AHqp-WhffvgtVx68fyMMLNuToGK6ArS8Yo1TL11AGS&_nc_ohc=_ffBl_dvzvcQ7kNvwE89Y3B&_nc_oc=AdqUeN-ZG2McrJ3YdHRZ6vkzkCNlMiRRlsID39UJNiyTNywK1s4HhniiHfIhRANWQ96yfWaaltki-QA2HuT47UyN&_nc_zt=23&_nc_ht=scontent.fsgn2-10.fna&_nc_gid=668Enl6x_091eVaP9szJRw&_nc_ss=793a8&oh=00_AQQw76X4HbDRmBbSNY0-mS6bXatCcybL9-fKpvhAGXoVuQ&oe=6B0B54A9"),
    ("11_black_blazer_white_bow_blouse.jpg", "Vest đen phối sơ mi trắng thắt nơ thanh lịch", "https://scontent.fsgn2-8.fna.fbcdn.net/v/t39.30808-6/482251558_9660619104001410_1413132883079917468_n.jpg?stp=dst-jpg_tt6&cstp=mx960x960&ctp=s960x960&_nc_cat=100&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeFZG2ycspzN7x5-UtkxX7MUvyZ4THeKAeW_JnhMd4oB5UJRIafGVuWhGkYbKRnFoGiWhrU6-n1vtzj5duNVTdfB&_nc_ohc=D7EbwwGyA28Q7kNvwEDyn7j&_nc_oc=AdrqGD11I_tB0QyHgrnRlDjQE1EUsWamhuCLZTsCM-a6nmeHrcMVXJlnLRYNp7OHChjgjAdJ3JhFf09Y2vo0kF-5&_nc_zt=23&_nc_ht=scontent.fsgn2-8.fna&_nc_gid=YyrvcgurPZ0GYRhHsPdlQw&_nc_ss=793a8&oh=00_AQQLK1Xqhu9Q3Z1-ZYWkEqpJHG2D3drF3zgBZckfX0J26A&oe=6B0B30BE"),
    ("12_white_suit_pink_rose_lifestyle.jpg", "Set trắng cầm hoa hồng phấn nhẹ nhàng nữ tính", "https://scontent.fsgn2-3.fna.fbcdn.net/v/t39.30808-6/484096549_9619917691404885_5047126519367660828_n.jpg?stp=dst-jpg_tt6&cstp=mx960x959&ctp=s960x959&_nc_cat=103&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=a5f93a&_nc_eui2=AeHD4uxrXeQlm9wrVwPeOq5kM53RDQs2DhozndENCzYOGkF3HvmONroievuMMLdKmBfHdc5FlsPcOop-3ZxJk6hy&_nc_ohc=Xrgc1qGdyDMQ7kNvwHc9H-M&_nc_oc=AdrUEuSke9tVJHHiy2Q7BbjONxM4ZF31obApl4H_o-TTqwJeiZrJf2yJto5ZxwdUtNXYulaoFNn3SqwN1jscU5VY&_nc_zt=23&_nc_ht=scontent.fsgn2-3.fna&_nc_gid=6E9mJ_NjEhg-mxF-EC8J3Q&_nc_ss=793a8&oh=00_AQT-ZuTOZKMgz3vOShvWnfDOH6wakrEVEkhIBGYOGZRvDg&oe=6B0B4F63"),
    ("13_nha_trang_resort_pink_maxi_lawn.jpg", "Nha Trang Resort — Đầm maxi hồng cánh sen & kính trắng dưới hàng dừa biển", "https://scontent.fsgn2-4.fna.fbcdn.net/v/t39.30808-6/656754572_26541937748776281_4776196361281063740_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x1365&ctp=s2048x1365&_nc_cat=101&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=f727a1&_nc_eui2=AeHmXv00RvKmYMEYpZw1RKtWvk8tx_WMQFm-Ty3H9YxAWRCjn6FL27LJ3UHCKefEhse3buOwRCjsL33SX3V9IlRw&_nc_ohc=s8MH9zK0QtMQ7kNvwEapXRb&_nc_oc=AdohCP19c8g4TkM7_N5UE2tiUdfGW2yEjiTbkYbuMse0-j2Qs9dJ63NxV1Sr3pOQd23E7jS6NvdJurZPN4e4SLRJ&_nc_zt=23&_nc_ht=scontent.fsgn2-4.fna&_nc_gid=YBEKh2dsakaj_Uf4TJ43yA&_nc_ss=793a8&oh=00_AQQjFNCFarAByFeeDFlP6K6mdVze2Pwu1xA9DipVMxmRpw&oe=6B0B50FD"),
    ("14_nha_trang_palm_garden_sunlit.jpg", "Thảm cỏ xanh mướt & rặng dừa Vinpearl/Marriott Nha Trang tràn nắng trong trẻo", "https://scontent.fsgn2-5.fna.fbcdn.net/v/t39.30808-6/654540453_26541930992110290_6612967921882097681_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x1365&ctp=s2048x1365&_nc_cat=106&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=f727a1&_nc_eui2=AeHnJhs1KjE6wdK_rVRbrIkVBGzzSkFYTwYEbPNKQVhPBkM6JqRIXYVUcqAb9llkjocoj-3-QsiOdGJLMJQ42a_l&_nc_ohc=pxjRx4IIi0YQ7kNvwGJ4FE3&_nc_oc=AdrRrqOBDPmgeJt32Bde4tvKCZtE9NU2DxzJdaes3An5ieGW-EnISb_yseNgiOJNP2jQqFxdbmp491zDRuJKltLm&_nc_zt=23&_nc_ht=scontent.fsgn2-5.fna&_nc_gid=6KsBCpuRjQ3S_mLBbz-5jA&_nc_ss=793a8&oh=00_AQTtXir9ROYQ5M9eWAuaBSdrNkVH-Nce0CFULXx7VofwLw&oe=6B0B500E"),
    ("15_nha_trang_golden_hour_breeze.jpg", "Nắng chiều vàng dịu trong trẻo tại khu nghỉ dưỡng biển Nha Trang", "https://scontent.fsgn2-7.fna.fbcdn.net/v/t39.30808-6/656010021_26541932512110138_8256792560359337531_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x1365&ctp=s2048x1365&_nc_cat=107&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=f727a1&_nc_eui2=AeECrM5SsofObMP6ihCiBAl5Hj8zNQE-UKMePzM1AT5Qo9kAvKUfFw1-Y6zvyK7AFoeBPX3l2FaLhwaDGoHQEGM0&_nc_ohc=BUMMgFiHEQ4Q7kNvwH53r8T&_nc_oc=AdoqTBuvQ7xk62bX4U9ztv0_FS_FtwJNRL8bKoKKXs-i05TtaooF0B9pn6yoQLKITOJjUC0i4MHzgJ_xvw3f58TW&_nc_zt=23&_nc_ht=scontent.fsgn2-7.fna&_nc_gid=iOv9EAL1SaI86xUm1qCHsA&_nc_ss=793a8&oh=00_AQQGwG7qsxzfkhJBdxv1FgFMbLAY6RoYVRmH87qq6WD8Ag&oe=6B0B577F"),
    ("16_nha_trang_white_architecture_resort.jpg", "Kiến trúc trắng tinh khôi & hàng cọ biển Vinpearl Nha Trang", "https://scontent.fsgn2-6.fna.fbcdn.net/v/t39.30808-6/657292360_26541925638777492_8598526600171916428_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x1365&ctp=s2048x1365&_nc_cat=105&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=f727a1&_nc_eui2=AeESdjYRihfcHi-LJvdi5XrAO_nlaTHB8dk7-eVpMcHx2bv5DdIBTwnW3NfGbbWpQDy368vKuIIfnSfK7h7pDvBK&_nc_ohc=GiAPkpOB1a8Q7kNvwEe2BJp&_nc_oc=AdoTTSKeGVJPSYL9NKLlFER4YGr61apzDK-reyZHzXDxsCh_xmhjpeATFD6cKwiki5wlvV7p5hWGwqeReOD1mqOt&_nc_zt=23&_nc_ht=scontent.fsgn2-6.fna&_nc_gid=ImOOyDEb9bmC2iLUcWWcRg&_nc_ss=793a8&oh=00_AQTBoaF9Wv0yzMgSi0j8sdEcF3JDHveyDf-_QImlKJyvXA&oe=6B0B33FB"),
]


HO_SO_MD = """# Hồ Sơ Nhân Vật & Phong Cách Sống Nha Trang — CEO Nguyễn Thị Hằng (`facebook.com/hang.thu.146`)

## 1. Thông Tin Định Danh Chuẩn Đời Thực
- **Họ và tên:** Nguyễn Thị Hằng (*Hang Thu*)
- **Link tham chiếu chính thức:** https://www.facebook.com/hang.thu.146 (`65K followers` · `15M Reel views`)
- **Chức danh chuẩn:** **CEO Hằng Thu Pharma** (Nhà sáng lập hệ thống 15.000+ thành viên từ 2012, đồng hành cùng **Hằng Thu Pharma** & **An Vượng Pharma**, thành viên lãnh đạo BNI tại Nha Trang).
- **Nơi sinh sống & bối cảnh xuyên suốt:** **Thành phố biển Nha Trang, Khánh Hòa** (quê gốc Vinh — Nghệ An, đã kết hôn, gia đình hạnh phúc 3 bé *Bông – Đậu – Cà Rốt*).
- **Châm ngôn & Giọng văn đặc trưng:**
  - *"Bán hàng bằng tâm · Thành công bằng giá trị"*
  - *"Kinh doanh bằng giá trị thật — Dẫn lối cộng đồng đến cuộc sống tốt đẹp hơn"*
  - Giọng chia sẻ gần gũi, năng lượng tích cực, vừa bản lĩnh của một nữ CEO dẫn dắt đội nhóm, vừa duyên dáng, đời thường của người phụ nữ hiện đại yêu gia đình và chăm sóc sức khỏe chủ động tại phố biển Nha Trang.

---

## 2. Quy Chuẩn Thẩm Mỹ Hình Ảnh Bắt Buộc: "TRONG TRẺO — NẮNG BIỂN NHA TRANG" (`Crystal-Clear Coastal Daylight`)
Mọi ảnh AI (ChatGPT `HTPM` / Gemini) và clip Video AI (Google Flow `Omni 1.2`) cho hệ thống **10 Video + 10 Thiết kế / ngày** bắt buộc khóa chặt bảng màu & ánh sáng sau:
1. **Ánh sáng trong trẻo (`High-Key Natural Sunlit Clarity`):**
   - Ánh nắng tự nhiên sáng trong của vùng biển Nha Trang (`5200K–5600K` ban mai hoặc `4800K` nắng chiều dịu), da trắng hồng mịn tự nhiên rõ kết cấu thật, mắt sáng long lanh, tuyệt đối **không ám vàng đục**, **không tối u ám**, **không đổ bóng gắt**, **không dùng chữ vàng 3D AI sến**.
2. **Hệ Bối Cảnh Sống & Làm Việc Đặc Trưng Tại Nha Trang (`10 Nhóm Bối Cảnh Xoay Vòng Mỗi Ngày`):**
   - **Bối cảnh 01 — Ban công Căn hộ / Penthouse hướng Vịnh Nha Trang:** Cửa kính lớn mở ra biển xanh ngọc bích dịu mắt & bầu trời mây trắng nắng sớm, rèm voan trắng bay nhẹ trong gió biển.
   - **Bối cảnh 02 — Quán Cà phê Sân vườn Nhiệt đới Nha Trang:** Không gian mở nhà kính thoáng đãng, lá cọ xanh mướt, nắng xuyên tán cây trong trẻo, ly trà hoa quả / nước ấm buổi sáng.
   - **Bối cảnh 03 — Khu Nghỉ dưỡng Vinpearl / Marriott Nha Trang:** Thảm cỏ xanh ngọc lục bảo, hàng dừa cao vút, kiến trúc biệt thự trắng tinh khôi ven biển.
   - **Bối cảnh 04 — Phòng Điều hành CEO Đá Trắng Cẩm Thạch:** Bàn marble sáng, ánh nắng cửa sổ rọi qua kính, hoa cẩm tú cầu / hoa ly trắng tinh tế.
   - **Bối cảnh 05 — Phòng Khách Villa Hiện Đại Đón Gió Biển:** Sofa kem/trắng thoáng sáng, bình hoa tươi, không gian gia đình ấm áp thanh lịch.
   - **Bối cảnh 06 — Đường Dạo Biển Trần Phú / Bến Du Thuyền Nha Trang Sáng Sớm:** Làn gió biển mát lành, nắng ban mai trong vắt, nhịp sống khỏe khoắn năng động.
   - **Bối cảnh 07 — Góc Bàn Trang Điểm & Chăm Sóc Bản Thân Buổi Tối Tinh Khôi:** Đèn ánh kem dịu nhẹ, lụa trắng ngọc trai, gương tròn thoáng sáng.
   - **Bối cảnh 08 — Góc Bếp Đảo Đá Trắng Dinh Dưỡng Gia Đình:** Trái cây nhiệt đới tươi mát, cốc nước ấm buổi sáng trước khi đi làm.
   - **Bối cảnh 09 — Không Gian Trà Chiều / Lounge Sang Trọng View Biển:** Ánh sáng tự nhiên dịu nhẹ, phong thái doanh nhân thư thái.
   - **Bối cảnh 10 — Sự Kiện / Hội Thảo Đào Tạo Đội Nhóm Sáng Sang:** Không gian hội trường trắng – xanh biển hiện đại tại khách sạn 5 sao Nha Trang.
3. **Tủ Đồ Đa Dạng Chuẩn Phong Cách Đời Thực Của Chị Hằng (`10 Phong Cách Không Trùng Lặp Trong Ngày`):**
   - Vest trắng kem khoác hờ vai + áo lụa cổ cao · Đầm vest trắng chiết eo · Suit đỏ đô quyền lực · Blazer màu kem BNI + chuỗi dây thanh mảnh · Đầm xanh băng pastel trễ vai · Sơ mi trắng thắt nơ cổ điển + chân váy · Đầm maxi hồng/trắng dạo resort biển Nha Trang · Vest xanh navy + ngọc trai · Suit xanh pastel/cốm tươi trẻ · Áo dài / đầm dạ hội thanh lịch cho dịp đặc biệt.
"""


def main():
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    downloaded = []
    for fname, desc, url in PHOTOS:
        dest = LOCAL_DIR / fname
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = resp.read()
            if len(data) > 15_000:
                dest.write_bytes(data)
                im = Image.open(dest)
                downloaded.append({"file": fname, "size": im.size, "bytes": len(data), "desc": desc})
                print(f"[OK] {fname} -> {im.size} ({len(data)} bytes)")
        except Exception as e:
            print(f"[WARN] Failed {fname}: {e}")

    for src_s, dst_name in SANDBOX_SHOTS:
        sp = Path(src_s)
        if sp.exists():
            shutil.copy2(sp, LOCAL_DIR / dst_name)

    (LOCAL_DIR / "HO_SO_NHAN_VAT_CHI_HANG_NHA_TRANG_FB.md").write_text(HO_SO_MD, encoding="utf-8")
    meta_json = {
        "character_name": "Nguyễn Thị Hằng",
        "role": "CEO Hằng Thu Pharma",
        "facebook_url": "https://www.facebook.com/hang.thu.146",
        "city": "Nha Trang, Khánh Hòa",
        "visual_style": "Crystal-clear coastal Nha Trang natural daylight, pure bright skin tone, airy ocean/garden/villa/marble-office backdrops, authentic wardrobe rotation",
        "daily_quota": {"videos_9x16": 10, "graphic_posts": 10},
        "downloaded_reference_photos": downloaded,
    }
    (LOCAL_DIR / "character_guidelines_nha_trang.json").write_text(
        json.dumps(meta_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Build a crisp 4x4 Reference Contact Sheet of Chị Hằng's real Facebook photos for quick visual preview!
    valid_imgs = [LOCAL_DIR / d["file"] for d in downloaded if (LOCAL_DIR / d["file"]).exists()]
    if valid_imgs:
        cols, rows = 4, min(4, (len(valid_imgs) + 3) // 4)
        cell_w, cell_h = 380, 380
        sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * 16, rows * cell_h + (rows + 1) * 16), (248, 251, 255))
        for idx, ip in enumerate(valid_imgs[: cols * rows]):
            im = ImageOps.fit(Image.open(ip).convert("RGB"), (cell_w, cell_h), Image.Resampling.LANCZOS)
            r, c = divmod(idx, cols)
            sheet.paste(im, (16 + c * (cell_w + 16), 16 + r * (cell_h + 16)))
        sheet_path = LOCAL_DIR / "BANG_16_ANH_MAU_CHI_HANG_NHA_TRANG_FB.jpg"
        sheet.save(sheet_path, quality=93)
        shutil.copy2(sheet_path, ARTIFACT_DIR / "fb_chi_hang_nha_trang_16_refs.jpg")

    # Sync to both Google Drive folders (GEMINI.md Rule #2.0)
    for gdir in (DRIVE_CUST_DIR, DRIVE_TLH_DIR):
        try:
            if Path(gdir.anchor).exists():
                gdir.mkdir(parents=True, exist_ok=True)
                for item in LOCAL_DIR.iterdir():
                    if item.is_file():
                        shutil.copy2(item, gdir / item.name)
                print(f"[SYNCED DRIVE] {gdir}")
        except Exception as e:
            print(f"[WARN DRIVE] {gdir}: {e}")

    print(f"[TOTAL DOWNLOADED] {len(downloaded)}/16 photos")


if __name__ == "__main__":
    main()
