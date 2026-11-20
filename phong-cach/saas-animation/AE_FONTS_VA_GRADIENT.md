# Bảng Tên PostScript 39 Font Tiếng Việt & 6 Preset Chữ Gradient Trong After Effects

Toàn bộ `39` font `.ttf` đã được cài vào Windows Fonts (`%LOCALAPPDATA%\Microsoft\Windows\Fonts`) nên **After Effects và Photoshop nhận diện tự động** qua đúng `postScriptName` dưới đây:

## 1. Cách gọi Chữ Gradient 4 điểm + Tách Viền Sau + Quét Ánh Kim (`saas-lib.jsx` v1.4.0 & `th-lib.jsx` v1.1)
```javascript
// Trong SaaS AE Kit (saas-lib.jsx):
var g = H.gradText(comp, {
  text: 'TỎA SÁNG RẠNG NGỜI', size: 84, font: H.FONT_VI.serifLuxury,
  pos: [960, 480], preset: 'gold_champagne', sw: 8, sweepT0: 0.4, sweepDur: 0.65
});
H.blurFocusIn(g.front, 0.1, 0.42, 26, 94);

// Trong Talking Head AE Kit (th-lib.jsx):
var kw = T.txt(comp, { text: 'ĐIỀU HÒA NỘI TIẾT', size: 136, font: T.FONT_VI.title, pos: [540, 440] });
T.gradPreset(comp, kw, 'rose_silk', 1.2, 0.6, 8);
```

## 2. Danh sách 39 Font Tiếng Việt Đã Kiểm Chứng 100% (`fonts_vi.py`)
```
OK   Alex Brush Regular [PS: AlexBrush-Regular]  (AlexBrush-Regular.ttf)
OK   Anton Regular [PS: Anton-Regular]  (Anton-Regular.ttf)
OK   Baloo 2 Bold [PS: Baloo2-Bold]  (Baloo2-Bold.ttf)
OK   Baloo 2 ExtraBold [PS: Baloo2-ExtraBold]  (Baloo2-ExtraBold.ttf)
OK   Be Vietnam Pro Bold [PS: BeVietnamPro-Bold]  (BeVietnamPro-Bold.ttf)
OK   Be Vietnam Pro ExtraBold [PS: BeVietnamPro-ExtraBold]  (BeVietnamPro-ExtraBold.ttf)
OK   Be Vietnam Pro Medium [PS: BeVietnamPro-Medium]  (BeVietnamPro-Medium.ttf)
OK   Be Vietnam Pro SemiBold [PS: BeVietnamPro-SemiBold]  (BeVietnamPro-SemiBold.ttf)
OK   Cormorant Garamond Bold [PS: CormorantGaramond-Bold]  (CormorantGaramond-Bold.ttf)
OK   Cormorant Garamond Bold Italic [PS: CormorantGaramond-BoldItalic]  (CormorantGaramond-BoldItalic.ttf)
OK   Cormorant Garamond SemiBold [PS: CormorantGaramond-SemiBold]  (CormorantGaramond-SemiBold.ttf)
OK   Dancing Script Bold [PS: DancingScript-Bold]  (DancingScript-Bold.ttf)
OK   Fraunces Black [PS: Fraunces-Black]  (Fraunces-Black.ttf)
OK   Fraunces Bold [PS: Fraunces-Bold]  (Fraunces-Bold.ttf)
OK   Great Vibes Regular [PS: GreatVibes-Regular]  (GreatVibes-Regular.ttf)
OK   Inter Medium [PS: Inter-Medium]  (Inter-Medium.ttf)
OK   Inter Regular [PS: Inter-Regular]  (Inter-Regular.ttf)
OK   Inter SemiBold [PS: Inter-SemiBold]  (Inter-SemiBold.ttf)
OK   Lora Bold [PS: Lora-Bold]  (Lora-Bold.ttf)
OK   Lora Italic [PS: Lora-Italic]  (Lora-Italic.ttf)
OK   Lora SemiBold [PS: Lora-SemiBold]  (Lora-SemiBold.ttf)
OK   Montserrat Black [PS: Montserrat-Black]  (Montserrat-Black.ttf)
OK   Montserrat Bold [PS: Montserrat-Bold]  (Montserrat-Bold.ttf)
OK   Montserrat ExtraBold [PS: Montserrat-ExtraBold]  (Montserrat-ExtraBold.ttf)
OK   Montserrat SemiBold [PS: Montserrat-SemiBold]  (Montserrat-SemiBold.ttf)
OK   Noto Serif Display Bold [PS: NotoSerifDisplay-Bold]  (NotoSerifDisplay-Bold.ttf)
OK   Noto Serif Display ExtraBold [PS: NotoSerifDisplay-ExtraBold]  (NotoSerifDisplay-ExtraBold.ttf)
OK   Oswald Bold [PS: Oswald-Bold]  (Oswald-Bold.ttf)
OK   Oswald SemiBold [PS: Oswald-SemiBold]  (Oswald-SemiBold.ttf)
OK   Paytone One Regular [PS: PaytoneOne-Regular]  (PaytoneOne-Regular.ttf)
OK   Playfair Display Bold [PS: PlayfairDisplay-Bold]  (PlayfairDisplay-Bold.ttf)
OK   Playfair Display Bold Italic [PS: PlayfairDisplay-BoldItalic]  (PlayfairDisplay-BoldItalic.ttf)
OK   Playfair Display ExtraBold [PS: PlayfairDisplay-ExtraBold]  (PlayfairDisplay-ExtraBold.ttf)
OK   Playfair Display Regular [PS: PlayfairDisplay-Regular]  (PlayfairDisplay-Regular.ttf)
OK   Plus Jakarta Sans Bold [PS: PlusJakartaSans-Bold]  (PlusJakartaSans-Bold.ttf)
OK   Plus Jakarta Sans ExtraBold [PS: PlusJakartaSans-ExtraBold]  (PlusJakartaSans-ExtraBold.ttf)
OK   Plus Jakarta Sans SemiBold [PS: PlusJakartaSans-SemiBold]  (PlusJakartaSans-SemiBold.ttf)
OK   Prata Regular [PS: Prata-Regular]  (Prata-Regular.ttf)
OK   Yeseva One Regular [PS: YesevaOne-Regular]  (YesevaOne-Regular.ttf)
```
